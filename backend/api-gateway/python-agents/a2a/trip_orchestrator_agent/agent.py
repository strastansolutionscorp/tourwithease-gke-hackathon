import asyncio
import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yaml
from pathlib import Path
from dotenv import load_dotenv
import uuid
import json

# ADD THESE IMPORTS FOR SESSION MANAGEMENT
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, Session
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory # Tool to query memory
from google.genai.types import Content, Part
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load environment variables
load_dotenv()

APP_NAME = "memory_example_app"
USER_ID = "mem_user"
MODEL = "gemini-2.0-flash"

# Load configuration
def load_config():
    config_path = Path(__file__).parent / "agent_config.yaml"
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {
            "name": "trip_orchestrator_agent",
            "port": 8001,
            "model": "gemini-2.0-flash",
            "description": "Intelligent travel orchestrator",
            "instruction": "You are a travel planning assistant.",
            "metadata": {},
            "model_config": {
                "temperature": 0.1,
                "top_p": 0.9,
                "max_output_tokens": 2048
            },
            "safety_settings": []
        }

config = load_config()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SPECIALIST AGENTS CONFIG
SPECIALIST_AGENTS = {
    "context_specialist": {
        "name": "context_specialist_agent", 
        "url": "http://localhost:8002",
        "description": "Travel context intelligence",
        "keywords": ["weather", "culture", "currency", "language", "customs", "visa", "climate", "local", "tradition", "destination"],
        "priority_score": 0.8
    },
    "flight_specialist": {
        "name": "flight_specialist_agent", 
        "url": "http://localhost:8003",
        "description": "Flight booking expert",
        "keywords": ["flight", "fly", "plane", "airline", "airport", "ticket", "departure", "arrival", "boarding"],
        "priority_score": 0.9
    },
    "hotel_specialist": {
        "name": "hotel_specialist_agent", 
        "url": "http://localhost:8004",
        "description": "Hotel and accommodation expert", 
        "keywords": ["hotel", "accommodation", "stay", "room", "lodge", "resort", "check-in", "booking"],
        "priority_score": 0.9
    }
}

# CREATE GLOBAL SESSION SERVICE FOR MEMORY
orchestrator_session_service = InMemorySessionService()

# PYDANTIC MODELS FOR API
class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = {}
    session_id: Optional[str] = None
    user_id: Optional[str] = "orchestrator_user"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    routing_info: Optional[dict] = {}
    timestamp: str

# ENHANCED SESSION-AWARE ROUTING FUNCTION
async def intelligent_agent_routing_with_session(
    user_message: str,
    session_context: Optional[Dict[str, Any]] = None,
    session_id: str = ""
) -> Dict[str, Any]:
    """Enhanced routing function with session context awareness"""
    
    logger.info(f"🧠 Session-aware routing for: {user_message}")
    logger.info(f"📋 Session context available: {bool(session_context)}")
    
    try:
        # STEP 1: Enhanced message analysis with session context
        routing_decision = await _analyze_message_with_context(user_message, session_context)
        
        if routing_decision["status"] != "success":
            return {
                "status": "error",
                "message": f"Message analysis failed: {routing_decision.get('error', 'Unknown error')}",
                "fallback_response": "I can help you plan your trip. Could you provide more specific details about what you need?"
            }
        
        selected_agent = routing_decision["selected_agent"]
        confidence = routing_decision["confidence"]
        reasoning = routing_decision["reasoning"]
        
        logger.info(f"🎯 Selected agent: {selected_agent} (confidence: {confidence})")
        
        # STEP 2: Check availability
        agent_info = SPECIALIST_AGENTS[selected_agent]
        is_available = await _check_agent_availability(agent_info["url"])
        
        if not is_available:
            logger.warning(f"⚠️ {selected_agent} not available, trying fallback")
            return await _provide_fallback_response(user_message, selected_agent)
        
        # STEP 3: Call specialist with enhanced context
        specialist_response = await _call_specialist_with_context(
            selected_agent, 
            user_message, 
            session_context,
            session_id
        )
        
        # STEP 4: Return result with session info
        return {
            "status": "success",
            "routing_metadata": {
                "selected_agent": selected_agent,
                "agent_name": agent_info["name"],
                "agent_url": agent_info["url"],
                "confidence": confidence,
                "reasoning": reasoning,
                "routing_timestamp": datetime.now().isoformat(),
                "specialist_available": is_available,
                "session_id": session_id,
                "context_used": bool(session_context)
            },
            "specialist_response": specialist_response,
            "formatted_response": _format_specialist_response(specialist_response, selected_agent, reasoning)
        }
        
    except Exception as e:
        logger.error(f"❌ Session-aware routing error: {e}")
        return await _provide_emergency_fallback(user_message, str(e))

# ENHANCED MESSAGE ANALYSIS WITH SESSION CONTEXT
async def _analyze_message_with_context(message: str, session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Enhanced message analysis that considers session history"""
    
    try:
        message_lower = message.lower()
        agent_scores = {}
        
        # Check for context continuity signals
        context_bonus = 0
        last_agent = None
        
        primary_keyword_score = 3
        secondary_keyword_score = 1
        
        if session_context:
            # Extract previous routing decisions from session history
            conversation_history = session_context.get('conversation_history', [])
            if conversation_history:
                last_interaction = conversation_history[-1]
                last_agent = last_interaction.get('routing_metadata', {}).get('selected_agent')
                logger.info(f"📜 Previous agent: {last_agent}")
            
            # Check for continuation phrases
            continuation_phrases = [
                "more", "another", "also", "what about", "and", "plus", "additionally",
                "show me more", "find another", "any other", "similar"
            ]
            
            for phrase in continuation_phrases:
                if phrase in message_lower:
                    context_bonus = 0.3  # Boost score for last used agent
                    logger.info(f"🔄 Detected continuation signal: '{phrase}'")
                    break
        
        # Calculate scores for each specialist
        for agent_key, agent_info in SPECIALIST_AGENTS.items():
            score = 0
            keywords = agent_info["keywords"]
            
            # Basic keyword matching
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
            
            # Pattern-based scoring (your existing logic)
            if agent_key == "hotel_specialist":
            # Keywords related to finding and booking lodging
                hotel_patterns = {
                    # Core Actions & Intents (High Score)
                    "book a hotel": primary_keyword_score, "find a hotel": primary_keyword_score, 
                    "reserve a room": primary_keyword_score, "need a place to stay": primary_keyword_score,
                    "check availability": primary_keyword_score, "room rates": primary_keyword_score,
                    # Core Nouns (High Score)
                    "hotel": primary_keyword_score, "motel": primary_keyword_score, 
                    "resort": primary_keyword_score, "accommodation": primary_keyword_score,
                    # Specific Lodging Types (Secondary Score)
                    "inn": secondary_keyword_score, "lodge": secondary_keyword_score, 
                    "guesthouse": secondary_keyword_score, "bed and breakfast": secondary_keyword_score,
                    "b&b": secondary_keyword_score, "vacation rental": secondary_keyword_score, 
                    "apartment": secondary_keyword_score, "villa": secondary_keyword_score,
                    # Logistics & Details (Secondary Score)
                    "check-in": secondary_keyword_score, "check-out": secondary_keyword_score, 
                    "booking": secondary_keyword_score, "reservation": secondary_keyword_score,
                    # Amenities & Features (Secondary Score)
                    "pet-friendly": secondary_keyword_score, "free parking": secondary_keyword_score, 
                    "with a pool": secondary_keyword_score, "gym": secondary_keyword_score, 
                    "free wifi": secondary_keyword_score, "breakfast included": secondary_keyword_score,
                    "sea view": secondary_keyword_score, "kitchenette": secondary_keyword_score,
                    # Problem & Change Management
                    "cancel my booking": primary_keyword_score, "change my reservation": primary_keyword_score
                }
                for pattern, value in hotel_patterns.items():
                    if pattern in message_lower:
                        score += value
                            
            elif agent_key == "flight_specialist":
                # Keywords related to air travel
                flight_patterns = {
                    # Core Actions & Intents (High Score)
                    "book a flight": primary_keyword_score, "find a flight": primary_keyword_score,
                    "fly to": primary_keyword_score, "fly from": primary_keyword_score, 
                    "get me to": primary_keyword_score, "search for airfare": primary_keyword_score,
                    # Core Nouns (High Score)
                    "flight": primary_keyword_score, "airline": primary_keyword_score, 
                    "airport": primary_keyword_score, "ticket": primary_keyword_score,
                    # Logistics & Details (Secondary Score)
                    "departure": secondary_keyword_score, "arrival": secondary_keyword_score, 
                    "one-way": secondary_keyword_score, "round trip": secondary_keyword_score,
                    "return ticket": secondary_keyword_score, "direct flight": secondary_keyword_score,
                    "non-stop": secondary_keyword_score, "layover": secondary_keyword_score, 
                    "connecting flight": secondary_keyword_score, "red-eye": secondary_keyword_score,
                    # Fare Classes & Services (Secondary Score)
                    "economy": secondary_keyword_score, "business class": secondary_keyword_score, 
                    "first class": secondary_keyword_score, "premium economy": secondary_keyword_score,
                    "upgrade my seat": secondary_keyword_score, "baggage allowance": secondary_keyword_score,
                    # Status & Management
                    "flight status": primary_keyword_score, "change my flight": primary_keyword_score, 
                    "cancel my flight": primary_keyword_score
                }
                for pattern, value in flight_patterns.items():
                    if pattern in message_lower:
                        score += value
                            
            elif agent_key == "context_specialist":
                # Keywords for destination information, culture, and practical advice
                context_patterns = {
                    # Weather (High Score)
                    "weather": primary_keyword_score, "forecast": primary_keyword_score, 
                    "temperature": primary_keyword_score, "is it sunny": primary_keyword_score,
                    "will it rain": primary_keyword_score, "climate": secondary_keyword_score,
                    # Currency & Money (High Score)
                    "currency": primary_keyword_score, "exchange rate": primary_keyword_score, 
                    "forex": primary_keyword_score, "convert money": primary_keyword_score, 
                    "atm": secondary_keyword_score, "cash": secondary_keyword_score,
                    # Culture & Experiences (High Score)
                    "culture": primary_keyword_score, "customs": primary_keyword_score, 
                    "traditions": primary_keyword_score, "local food": primary_keyword_score,
                    "what to eat": primary_keyword_score, "cuisine": primary_keyword_score,
                    "attractions": primary_keyword_score, "landmarks": primary_keyword_score,
                    "what to see": primary_keyword_score, "things to do": primary_keyword_score,
                    # Practical Info (Secondary Score)
                    "language": secondary_keyword_score, "visa": secondary_keyword_score, 
                    "safety": secondary_keyword_score, "is it safe": secondary_keyword_score,
                    "local transport": secondary_keyword_score, "tipping culture": secondary_keyword_score,
                    "what to pack": secondary_keyword_score, "power outlet": secondary_keyword_score,
                    # General Queries (Secondary Score)
                    "about": secondary_keyword_score, "tell me about": secondary_keyword_score, 
                    "info on": secondary_keyword_score
                }
                for pattern, value in context_patterns.items():
                    if pattern in message_lower:
                        score += value
            
            # Apply context bonus if this was the last used agent
            if last_agent == agent_key and context_bonus > 0:
                score += context_bonus
                logger.info(f"🎯 Context bonus applied to {agent_key}: +{context_bonus}")
            
            # Apply priority multiplier
            score *= agent_info["priority_score"]
            agent_scores[agent_key] = score
        
        # Find best agent
        if not agent_scores or max(agent_scores.values()) == 0:
            selected_agent = "context_specialist"
            confidence = 0.5
            reasoning = "No specific domain detected, routing to context specialist"
        else:
            selected_agent = max(agent_scores, key=agent_scores.get)
            max_score = agent_scores[selected_agent]
            total_score = sum(agent_scores.values())
            confidence = min(max_score / max(total_score, 1), 1.0)
            
            context_note = f" (with session context bonus)" if context_bonus > 0 and last_agent == selected_agent else ""
            reasoning = f"Selected based on keyword analysis{context_note}. Scores: {agent_scores}"
        
        return {
            "status": "success",
            "selected_agent": selected_agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "all_scores": agent_scores,
            "context_used": bool(session_context),
            "last_agent": last_agent
        }
        
    except Exception as e:
        logger.error(f"❌ Context-aware message analysis error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# ENHANCED SPECIALIST CALLING WITH CONTEXT
async def _call_specialist_with_context(agent_key: str, user_message: str, 
                                      session_context: Optional[Dict[str, Any]] = None,
                                      session_id: str = None) -> Dict[str, Any]:
    """Call specialist agent with enhanced session context"""
    
    try:
        agent_info = SPECIALIST_AGENTS[agent_key]
        agent_url = agent_info["url"]
        
        # Enhanced payload with session context
        payload = {
            "message": user_message,
            "context": session_context or {},
            "session_id": session_id or f"orchestrator_session_{uuid.uuid4()}",
            "routing_metadata": {
                "routed_from": "trip_orchestrator",
                "routing_method": "intelligent_analysis_with_context",
                "timestamp": datetime.now().isoformat(),
                "session_context_available": bool(session_context)
            }
        }
        
        logger.info(f"🔌 Calling {agent_key} at {agent_url} with session context")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{agent_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ {agent_key} responded successfully")
                return {
                    "status": "success",
                    "agent": agent_key,
                    "response": result
                }
            else:
                logger.error(f"❌ {agent_key} returned {response.status_code}")
                return {
                    "status": "error", 
                    "agent": agent_key,
                    "error": f"HTTP {response.status_code}"
                }
                
    except Exception as e:
        logger.error(f"❌ Error calling {agent_key}: {e}")
        return {
            "status": "error", 
            "agent": agent_key,
            "error": str(e)
        }

# Keep your existing helper functions
async def _check_agent_availability(agent_url: str) -> bool:
    """Check if specialist agent is available"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{agent_url}/health")
            return response.status_code == 200
    except:
        return False

async def _provide_fallback_response(user_message: str, unavailable_agent: str) -> Dict[str, Any]:
    """Provide helpful fallback when specialist is unavailable"""
    
    agent_descriptions = {
        "hotel_specialist": "hotel search and booking",
        "flight_specialist": "flight search and booking", 
        "context_specialist": "destination information and travel context"
    }
    
    service = agent_descriptions.get(unavailable_agent, "travel planning")
    
    fallback_message = f"""I understand you're looking for {service} assistance. 

Unfortunately, my {unavailable_agent.replace('_', ' ')} is currently unavailable, but I can still help you with general travel planning advice.

Please try again in a moment or let me know how else I can help with your travel planning."""

    return {
        "status": "fallback",
        "message": fallback_message,
        "unavailable_agent": unavailable_agent
    }

async def _provide_emergency_fallback(user_message: str, error: str) -> Dict[str, Any]:
    """Emergency fallback when routing completely fails"""
    
    return {
        "status": "emergency_fallback",
        "message": "I'm experiencing technical difficulties but I'm still here to help with your travel planning. Please try rephrasing your request.",
        "error_logged": error
    }

def _format_specialist_response(specialist_response: Dict[str, Any], agent_type: str, reasoning: str) -> str:
    """
    Intelligently formats the full JSON response from a specialist agent 
    into a markdown string for the orchestrator to summarize.
    """
    if specialist_response.get("status") != "success":
        return f"I encountered an issue coordinating with the {agent_type.replace('_', ' ')}: {specialist_response.get('error', 'Unknown error')}"

    response_data = specialist_response.get("response", {})
    if not isinstance(response_data, dict):
        # If the response is just a string, return it directly.
        return response_data

    formatted_parts = []
    
    # --- Custom Formatting for Each Specialist ---

    if agent_type == "hotel_specialist":
        hotels = response_data.get("hotels", [])
        if hotels:
            formatted_parts.append("Here are the top hotel options I found:")
            for i, hotel in enumerate(hotels[:5]): # Limit to top 5 for brevity
                name = hotel.get('name', 'N/A')
                price = hotel.get('offers', [{}])[0].get('price', {}).get('total', 'N/A')
                rating = hotel.get('rating', 'N/A')
                amenities = ", ".join(hotel.get('amenities', []))
                formatted_parts.append(f"{i+1}. **{name}** - Rating: {rating}/5, Price: ${price}, Amenities: {amenities}")
    
    elif agent_type == "flight_specialist":
        flights = response_data.get("flights", [])
        if flights:
            formatted_parts.append("Here are the best flight options I found:")
            for i, flight in enumerate(flights[:5]):
                airline = flight.get('airline', 'N/A')
                departure = flight.get('departure_time', 'N/A')
                arrival = flight.get('arrival_time', 'N/A')
                price = flight.get('price', 'N/A')
                formatted_parts.append(f"{i+1}. **{airline}** - Departs: {departure}, Arrives: {arrival}, Price: ${price}")

    elif agent_type == "context_specialist":
        # Context specialist might return various keys
        if "weather" in response_data:
            formatted_parts.append(f"**Weather:** {response_data['weather']}")
        if "currency" in response_data:
            formatted_parts.append(f"**Currency:** {response_data['currency']}")
        if "culture_tip" in response_data:
            formatted_parts.append(f"**Cultural Tip:** {response_data['culture_tip']}")

    # --- Fallback for any other text or generic response ---
    if "response" in response_data and isinstance(response_data["response"], str):
        # Check if this text is already in the formatted parts to avoid duplication
        if not any(response_data["response"] in part for part in formatted_parts):
            formatted_parts.append(response_data["response"])

    if not formatted_parts:
        # If no specific keys were found, provide a clean dump of the data
        return f"The specialist provided the following data:\n```json\n{json.dumps(response_data, indent=2)}\n```"

    return "\n".join(formatted_parts)


# CREATE ORCHESTRATOR AGENT WITH SESSION MANAGEMENT
trip_orchestrator_agent = LlmAgent(
    name=config["name"],
    model=config["model"],
    tools=[intelligent_agent_routing_with_session],
    instruction=f"""You are an intelligent Trip Orchestrator and **Response Synthesizer**. Your primary role is to interpret the structured data (JSON) returned by specialist agents and present it as a comprehensive, easy-to-read summary for the user.

**CORE WORKFLOW**:
1.  **Use the Tool:** For ALL travel-related queries, you MUST use the `intelligent_agent_routing_with_session` tool.
2.  **Receive Data:** The tool will return a detailed response from a specialist agent (e.g., a list of hotels, flight options, weather data).
3.  **Synthesize and Summarize:** Your main job is to **analyze this data and format it clearly**. DO NOT just pass through the raw text. If you receive a list of items, present them as a formatted list with key details.
4.  **Anticipate Next Steps:** After presenting the information, proactively suggest a logical next action. For example, after showing hotels, ask "Would you like me to book one of these for you, or perhaps check for flights to that destination?"

**RESPONSE GUIDELINES**:
*   **For Hotel Lists:** Present as a numbered list. For each hotel, clearly state the name, rating, price, and any key amenities.
*   **For Flight Lists:** Present as a numbered list. For each flight, show the airline, departure/arrival times, duration, and price.
*   **For Contextual Info:** Use headings for different topics like "Weather Forecast," "Currency Information," or "Cultural Tips."
*   **Maintain Tone:** Always be friendly, helpful, and act as a knowledgeable lead travel consultant.

**FORBIDDEN ACTIONS**:
*   You MUST NOT simply output the raw text from the specialist. Your value is in summarizing and clarifying the data.
*   You MUST NOT invent information. Your summary must be based entirely on the data provided by the specialist tool.

Use `intelligent_agent_routing_with_session` first, then synthesize the results beautifully!
""",
    description="Intelligent travel orchestrator that synthesizes specialist data into comprehensive user responses."
)

root_agent = trip_orchestrator_agent

# ENHANCED FASTAPI APP WITH SESSION MANAGEMENT
app = FastAPI(
    title="Trip Orchestrator with Session Memory",
    version="2.0.0",
    description="Intelligent travel orchestrator with conversation memory"
)

@app.post("/chat")
async def enhanced_chat_endpoint(request: ChatRequest):
    """Enhanced chat endpoint with session management"""
    
    try:
        session_id = request.session_id or f"orchestrator_session_{uuid.uuid4()}"
        user_id = request.user_id or "orchestrator_user"
        app_name = "trip_orchestrator_app"
        
        logger.info(f"💬 Chat request - Session: {session_id}, User: {user_id}")
        
        # Create runner with session service
        runner = Runner(
            agent=trip_orchestrator_agent,
            app_name=app_name,
            session_service=orchestrator_session_service
        )
        
        # Ensure session exists
        try:
            session_data = await orchestrator_session_service.get_session(app_name, user_id, session_id)
        except:
            logger.info(f"🆕 Creating new session: {session_id}")
            await orchestrator_session_service.create_session(app_name, user_id, session_id)
            session_data = None
        
        # Create message content
        content = Content(
            role='user',
            parts=[Part(text=request.message)]
        )
        
        # Run agent and collect response
        response_text = ""
        routing_info = {}
        
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.get_function_calls():
                for call in event.get_function_calls():
                    logger.info(f"🔧 Function called: {call.name}")
            
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text.strip()
        
        return ChatResponse(
            response=response_text,
            session_id=session_id,
            routing_info=routing_info,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Enhanced chat endpoint error: {e}")
        return ChatResponse(
            response=f"I encountered an error processing your request: {str(e)}. Please try again.",
            session_id=session_id,
            routing_info={"error": str(e)},
            timestamp=datetime.now().isoformat()
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": config["name"],
        "version": "2.0.0",
        "session_management": "enabled",
        "specialists_configured": list(SPECIALIST_AGENTS.keys()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, user_id: str = "orchestrator_user"):
    """Get conversation history for a session"""
    try:
        session_data = await orchestrator_session_service.get_session(
            "trip_orchestrator_app", user_id, session_id
        )
        return {"session_id": session_id, "history": session_data}
    except Exception as e:
        return {"error": f"Session not found: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.get("port", 8001))