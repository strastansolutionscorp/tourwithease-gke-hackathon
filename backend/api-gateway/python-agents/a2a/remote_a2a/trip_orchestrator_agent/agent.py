# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

import asyncio
import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yaml
from pathlib import Path
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from starlette.responses import JSONResponse

# Load environment variables
load_dotenv()

# Load configuration
def load_config():
    config_path = Path(__file__).parent / "agent_config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Available specialist agents configuration (FIXED PORT NUMBERS)
SPECIALIST_AGENTS = {
    "context_specialist": {
        "name": "context_specialist_agent", 
        "url": "http://localhost:8004",  # Context specialist port
        "description": "Travel context intelligence (weather, culture, destinations)",
        "keywords": ["weather", "culture", "currency", "language", "customs", "visa", "climate", "local", "tradition", "season", "temperature", "rain", "exchange", "destination info"],
        "priority_score": 0.8
    },
    "flight_specialist": {
        "name": "flight_specialist_agent", 
        "url": "http://localhost:8003",  # Flight specialist port
        "description": "Aviation and flight booking expert",
        "keywords": ["flight", "fly", "plane", "airline", "airport", "ticket", "departure", "arrival", "boarding", "gate", "seat", "baggage", "terminal", "runway"],
        "priority_score": 0.9
    },
    "hotel_specialist": {
        "name": "hotel_specialist_agent", 
        "url": "http://localhost:8005",  # Hotel specialist port (FIXED)
        "description": "Accommodation and hospitality expert", 
        "keywords": ["hotel", "accommodation", "stay", "room", "lodge", "resort", "check-in", "booking", "bed", "suite", "amenities", "concierge", "housekeeping"],
        "priority_score": 0.9
    }
}

async def intelligent_agent_routing(
    user_message: str,
    context: Optional[Dict[str, Any]] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Intelligently route user message to the most appropriate specialist agent
    
    This is the main routing function that analyzes the user's message and 
    automatically selects and calls the best specialist agent.
    
    Args:
        user_message: User's travel-related message
        context: Optional additional context
        tool_context: Tool context for state management
        
    Returns:
        Response from the selected specialist agent with routing metadata
    """
    logger.info(f"Intelligent routing for message: {user_message}")
    
    try:
        # Analyze message to determine best agent
        routing_decision = await _analyze_message_for_routing(user_message, context)
        
        if routing_decision["status"] != "success":
            return {
                "status": "error",
                "message": "Failed to analyze message for routing",
                "routing_decision": routing_decision
            }
        
        selected_agent = routing_decision["selected_agent"]
        confidence = routing_decision["confidence"]
        reasoning = routing_decision["reasoning"]
        
        logger.info(f"Selected agent: {selected_agent} (confidence: {confidence:.2f})")
        
        # Route to the selected specialist agent
        specialist_response = await _call_specialist_agent(
            selected_agent, 
            user_message, 
            context, 
            tool_context
        )
        
        # Store routing history
        if tool_context:
            if 'intelligent_routing_history' not in tool_context.state:
                tool_context.state['intelligent_routing_history'] = []
            
            tool_context.state['intelligent_routing_history'].append({
                'user_message': user_message,
                'selected_agent': selected_agent,
                'confidence': confidence,
                'reasoning': reasoning,
                'response_status': specialist_response.get('status', 'unknown'),
                'timestamp': datetime.now().isoformat()
            })
        
        return {
            "status": "success",
            "routing_metadata": {
                "selected_agent": selected_agent,
                "agent_name": SPECIALIST_AGENTS[selected_agent]["name"],
                "confidence": confidence,
                "reasoning": reasoning,
                "routing_timestamp": datetime.now().isoformat()
            },
            "specialist_response": specialist_response
        }
        
    except Exception as e:
        logger.error(f"Intelligent routing error: {e}")
        return {
            "status": "error",
            "message": f"Intelligent routing failed: {str(e)}"
        }

async def _analyze_message_for_routing(
    message: str, 
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Analyze user message to determine the best specialist agent"""
    try:
        message_lower = message.lower()
        agent_scores = {}
        
        # Score each specialist agent based on keyword matching
        for agent_key, agent_info in SPECIALIST_AGENTS.items():
            score = 0
            matched_keywords = []
            
            # Keyword matching with weighted scoring
            for keyword in agent_info["keywords"]:
                if keyword in message_lower:
                    # Weight longer keywords more heavily
                    keyword_weight = len(keyword.split()) * 1.5
                    score += keyword_weight
                    matched_keywords.append(keyword)
            
            # Apply priority multiplier
            score *= agent_info["priority_score"]
            
            agent_scores[agent_key] = {
                "score": score,
                "matched_keywords": matched_keywords,
                "agent_info": agent_info
            }
        
        # Advanced pattern matching for complex queries
        agent_scores = await _apply_advanced_routing_patterns(message_lower, agent_scores)
        
        # Select the best agent
        if not agent_scores or all(data["score"] == 0 for data in agent_scores.values()):
            # Default to context specialist for general queries
            selected_agent = "context_specialist"
            confidence = 0.3
            reasoning = "General travel query - defaulting to context specialist"
        else:
            # Sort by score and select the highest
            sorted_agents = sorted(
                agent_scores.items(), 
                key=lambda x: x[1]["score"], 
                reverse=True
            )
            
            selected_agent = sorted_agents[0][0]
            best_score = sorted_agents[0][1]["score"]
            matched_keywords = sorted_agents[0][1]["matched_keywords"]
            
            # Calculate confidence based on score and keyword matches
            confidence = min(best_score / 10.0, 1.0)  # Normalize to 0-1
            reasoning = f"Matched keywords: {', '.join(matched_keywords[:3])}" if matched_keywords else "Pattern-based selection"
        
        return {
            "status": "success",
            "selected_agent": selected_agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "agent_scores": {k: v["score"] for k, v in agent_scores.items()}
        }
        
    except Exception as e:
        logger.error(f"Message analysis error: {e}")
        return {
            "status": "error",
            "message": f"Message analysis failed: {str(e)}"
        }

async def _apply_advanced_routing_patterns(
    message_lower: str, 
    agent_scores: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Apply advanced pattern matching for better routing decisions"""
    
    # Pattern 1: Question types
    if any(word in message_lower for word in ["what's", "what is", "how's", "how is"]):
        if "weather" in message_lower or "climate" in message_lower:
            agent_scores["context_specialist"]["score"] += 3.0
        elif "price" in message_lower or "cost" in message_lower:
            if "flight" in message_lower:
                agent_scores["flight_specialist"]["score"] += 3.0
            elif "hotel" in message_lower:
                agent_scores["hotel_specialist"]["score"] += 3.0
    
    # Pattern 2: Action intentions
    if any(word in message_lower for word in ["book", "reserve", "buy", "purchase"]):
        if "flight" in message_lower:
            agent_scores["flight_specialist"]["score"] += 4.0
        elif "hotel" in message_lower or "room" in message_lower:
            agent_scores["hotel_specialist"]["score"] += 4.0
    
    # Pattern 3: Information seeking
    if any(word in message_lower for word in ["tell me about", "information about", "details about"]):
        agent_scores["context_specialist"]["score"] += 2.0
    
    # Pattern 4: Comparison requests
    if any(word in message_lower for word in ["compare", "vs", "versus", "better", "best"]):
        if "flight" in message_lower:
            agent_scores["flight_specialist"]["score"] += 2.0
        elif "hotel" in message_lower:
            agent_scores["hotel_specialist"]["score"] += 2.0
    
    # Pattern 5: Location-specific queries
    if any(word in message_lower for word in ["in", "at", "near"]):
        # Context for location-based questions
        agent_scores["context_specialist"]["score"] += 1.0
    
    return agent_scores

async def _call_specialist_agent(
    agent_key: str,
    user_message: str, 
    context: Optional[Dict[str, Any]] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Call the selected specialist agent"""
    try:
        agent_info = SPECIALIST_AGENTS[agent_key]
        agent_url = agent_info["url"]
        
        # Check if agent is available
        if not await _check_agent_availability(agent_url):
            return {
                "status": "error",
                "message": f"Agent '{agent_info['name']}' is currently unavailable",
                "fallback_needed": True
            }
        
        # Prepare enhanced request payload
        payload = {
            "message": user_message,
            "context": context or {},
            "routing_metadata": {
                "routed_from": "trip_orchestrator",
                "routing_method": "intelligent_analysis",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Make the request to specialist agent
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{agent_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error calling {agent_key}: {e}")
        return {
            "status": "error",
            "message": f"Failed to communicate with {agent_key}: {str(e)}",
            "fallback_needed": True
        }
    except Exception as e:
        logger.error(f"Error calling {agent_key}: {e}")
        return {
            "status": "error", 
            "message": f"Specialist agent call failed: {str(e)}",
            "fallback_needed": True
        }

async def _check_agent_availability(agent_url: str) -> bool:
    """Check if a specialist agent is available"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{agent_url}/health")
            return response.status_code == 200
    except:
        return False

# Trip planning functions (keeping all of them)
async def plan_trip_from_request(
    user_request: str,
    context: Optional[Dict[str, Any]] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Analyze user request and create a comprehensive travel plan"""
    logger.info(f"Planning trip from request: {user_request}")
    
    try:
        request_lower = user_request.lower()
        
        # Initialize trip plan
        plan = {
            "needs_flights": any(word in request_lower for word in 
                               ["flight", "fly", "plane", "travel to", "go to", "visit"]),
            "needs_hotels": any(word in request_lower for word in 
                              ["hotel", "stay", "accommodation", "room", "lodge"]),
            "needs_context": True,
            "trip_type": "leisure",
            "urgency": "normal",
            "destination": None,
            "origin": None,
            "departure_date": None,
            "return_date": None,
            "passengers": 1,
            "duration_days": None
        }
        
        # Extract destination
        if " to " in request_lower:
            parts = request_lower.split(" to ")
            if len(parts) > 1:
                destination_part = parts[-1].strip()
                dest_words = destination_part.split()
                if dest_words:
                    plan["destination"] = dest_words[0].capitalize()
                    
        # Extract origin if mentioned
        if " from " in request_lower:
            from_parts = request_lower.split(" from ")
            if len(from_parts) > 1:
                origin_part = from_parts[-1].split(" to ")[0].strip()
                origin_words = origin_part.split()
                if origin_words:
                    plan["origin"] = origin_words[0].upper()
        
        # Extract dates
        if "tomorrow" in request_lower:
            plan["departure_date"] = (datetime.now() + timedelta(days=1)).isoformat()[:10]
        elif "next week" in request_lower:
            plan["departure_date"] = (datetime.now() + timedelta(days=7)).isoformat()[:10]
        elif "next month" in request_lower:
            plan["departure_date"] = (datetime.now() + timedelta(days=30)).isoformat()[:10]
        
        # Extract number of passengers
        import re
        passenger_match = re.search(r'(\d+)\s*(people|person|passenger|traveler)', request_lower)
        if passenger_match:
            plan["passengers"] = int(passenger_match.group(1))
            
        # Determine trip type
        if any(word in request_lower for word in ["romantic", "honeymoon", "anniversary", "couple"]):
            plan["trip_type"] = "romantic"
        elif any(word in request_lower for word in ["business", "work", "meeting", "conference"]):
            plan["trip_type"] = "business"
        elif any(word in request_lower for word in ["family", "kids", "children", "child"]):
            plan["trip_type"] = "family"
        
        # Determine urgency
        if any(word in request_lower for word in ["urgent", "asap", "immediately", "soon"]):
            plan["urgency"] = "high"
        elif any(word in request_lower for word in ["flexible", "whenever", "no rush"]):
            plan["urgency"] = "low"
            
        # Store in context
        if tool_context:
            if 'trip_plans' not in tool_context.state:
                tool_context.state['trip_plans'] = []
            tool_context.state['trip_plans'].append({
                'user_request': user_request,
                'parsed_plan': plan,
                'timestamp': datetime.now().isoformat()
            })
        
        logger.info(f"Trip plan created: {plan}")
        
        coordination_results = await _coordinate_with_specialists(plan, tool_context)
        
        plan["specialist_results"] = coordination_results
        plan["coordination_status"] = "completed"
        return plan
        
    except Exception as e:
        logger.error(f"Trip planning error: {e}")
        return {
            "error": f"Trip planning failed: {str(e)}",
            "needs_flights": False,
            "needs_hotels": False,
            "needs_context": True
        }

async def _coordinate_with_specialists(plan: Dict[str, Any], tool_context: ToolContext) -> Dict[str, Any]:
    """Coordinate with specialist agents based on trip plan"""
    results = {}
    tasks = []
    
    # Prepare tasks for parallel execution using SPECIALIST_AGENTS config
    if plan.get("needs_flights") and plan.get("destination"):
        flight_task = _request_specialist_service(
            SPECIALIST_AGENTS["flight_specialist"]["url"],
            f"Search flights from {plan.get('origin', 'NYC')} to {plan.get('destination')} "
            f"on {plan.get('departure_date')} for {plan.get('passengers', 1)} passengers, "
            f"{plan.get('trip_type', 'leisure')} trip"
        )
        tasks.append(("flights", flight_task))
    
    if plan.get("needs_hotels") and plan.get("destination"):
        hotel_task = _request_specialist_service(
            SPECIALIST_AGENTS["hotel_specialist"]["url"],
            f"Search hotels in {plan.get('destination')} "
            f"check-in {plan.get('departure_date')} for {plan.get('passengers', 1)} guests, "
            f"{plan.get('trip_type', 'leisure')} trip"
        )
        tasks.append(("hotels", hotel_task))
    
    # Always get context for the destination
    if plan.get("destination"):
        context_task = _request_specialist_service(
            SPECIALIST_AGENTS["context_specialist"]["url"],
            f"Provide complete travel context for {plan.get('destination')} "
            f"for a {plan.get('trip_type', 'leisure')} trip on {plan.get('departure_date', 'flexible dates')}"
        )
        tasks.append(("context", context_task))
    
    # Execute all tasks in parallel
    if tasks:
        try:
            task_results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
            for i, (task_name, _) in enumerate(tasks):
                if isinstance(task_results[i], Exception):
                    results[task_name] = {
                        "status": "error", 
                        "error": str(task_results[i])
                    }
                else:
                    results[task_name] = task_results[i]
        except Exception as e:
            logger.error(f"Error coordinating with specialists: {e}")
            results["coordination_error"] = str(e)
    
    return results

async def _request_specialist_service(agent_url: str, message: str) -> Dict[str, Any]:
    """Generic specialist service request"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{agent_url}/chat",
                json={
                    "message": message,
                    "routing_metadata": {
                        "coordinated_by": "trip_orchestrator_agent",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error requesting specialist service from {agent_url}: {e}")
        return {"status": "error", "message": str(e)}

async def analyze_trip_prices(
    options: List[Dict[str, Any]], 
    criteria: Optional[Dict[str, Any]] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Analyze travel prices across different options"""
    if not options:
        return {"status": "no_data", "message": "No options to analyze"}

    try:
        prices = []
        for option in options:
            price = (option.get("price") or 
                    option.get("price_per_night") or 
                    option.get("total_cost") or 0)
            try:
                prices.append(float(price))
            except (ValueError, TypeError):
                continue

        if not prices:
            return {"status": "no_prices", "message": "No valid price data available"}

        analysis = {
            "status": "success",
            "price_range": {
                "min": min(prices),
                "max": max(prices),
                "average": sum(prices) / len(prices),
                "median": sorted(prices)[len(prices)//2] if prices else 0
            },
            "recommendations": [],
            "savings_opportunities": []
        }

        min_price_idx = prices.index(min(prices))
        analysis["recommendations"].append({
            "type": "best_value",
            "option_index": min_price_idx,
            "reason": "Lowest price option",
            "potential_savings": max(prices) - min(prices) if len(prices) > 1 else 0
        })

        if len(prices) > 2:
            sorted_with_indices = sorted(enumerate(prices), key=lambda x: x[1])
            mid_idx = sorted_with_indices[len(sorted_with_indices)//2][0]
            analysis["recommendations"].append({
                "type": "balanced",
                "option_index": mid_idx,
                "reason": "Good balance of price and quality"
            })

            price_spread = max(prices) - min(prices)
            if price_spread > 200:
                analysis["savings_opportunities"].append(
                    f"You could save up to ${price_spread:.0f} by choosing the budget option"
                )

        if tool_context:
            if 'price_analyses' not in tool_context.state:
                tool_context.state['price_analyses'] = []
            tool_context.state['price_analyses'].append({
                'analysis_result': analysis,
                'options_analyzed': len(options),
                'timestamp': datetime.now().isoformat()
            })

        return analysis

    except Exception as e:
        logger.error(f"Price analysis error: {e}")
        return {
            "status": "error",
            "message": f"Price analysis failed: {str(e)}"
        }

async def coordinate_travel_booking(
    booking_type: str,
    booking_details: Dict[str, Any],
    passenger_info: Dict[str, Any],
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Coordinate travel booking across multiple services"""
    logger.info(f"Coordinating {booking_type} booking")
    
    try:
        api_key = os.getenv('AWS_API_KEY')
        base_url = os.getenv('AWS_API_GATEWAY_URL')
        
        if not api_key or not base_url:
            return {
                "status": "success",
                "booking_reference": f"DEMO-{booking_type.upper()}-{datetime.now().strftime('%Y%m%d%H%M')}",
                "confirmation": f"Mock booking confirmed for {booking_type}",
                "details": {
                    "booking_type": booking_type,
                    "created_date": datetime.now().isoformat(),
                    "passenger_count": len(passenger_info.get("passengers", [passenger_info])),
                    "total_cost": booking_details.get("total_cost", 0)
                },
                "note": "Demo booking - AWS Lambda not configured"
            }
        
        payload = {
            "booking_type": booking_type,
            "booking_details": booking_details,
            "passenger_info": passenger_info
        }
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
        
        url = f"{base_url}/create-booking"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if tool_context:
                if 'bookings' not in tool_context.state:
                    tool_context.state['bookings'] = []
                tool_context.state['bookings'].append({
                    'booking_reference': result.get("booking_reference"),
                    'booking_type': booking_type,
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                "status": "success",
                "booking_reference": result.get("booking_reference"),
                "confirmation": result.get("confirmation"),
                "details": result
            }
            
    except Exception as e:
        logger.error(f"Booking coordination error: {e}")
        return {
            "status": "error",
            "message": f"Booking failed: {str(e)}",
            "booking_details": booking_details
        }

async def get_trip_recommendations(
    destination: str,
    trip_type: str = "leisure",
    budget: Optional[float] = None,
    duration: Optional[int] = None,
    tool_context: ToolContext = None
) -> str:
    """Get comprehensive trip recommendations"""
    logger.info(f"Getting trip recommendations for {destination} ({trip_type})")
    
    try:
        recommendations = []
        
        if trip_type == "romantic":
            recommendations.extend([
                f"For a romantic trip to {destination}:",
                "• Book evening flights for a more relaxed arrival",
                "• Choose boutique hotels or luxury properties with spa services",
                "• Look for restaurants with intimate ambiance and city views",
                "• Plan activities like sunset walks, couples' spa treatments, or wine tastings"
            ])
        elif trip_type == "business":
            recommendations.extend([
                f"For business travel to {destination}:",
                "• Choose morning flights to maximize business hours",
                "• Stay at business hotels near commercial districts",
                "• Book hotels with business centers, meeting rooms, and reliable WiFi",
                "• Consider express check-in services and airport transfers"
            ])
        elif trip_type == "family":
            recommendations.extend([
                f"For a family trip to {destination}:",
                "• Book family-friendly airlines with entertainment systems",
                "• Choose hotels with pools, kids' clubs, and connecting rooms",
                "• Look for destinations with family attractions and safe neighborhoods",
                "• Plan activities suitable for all ages and pack entertainment for travel"
            ])
        else:
            recommendations.extend([
                f"For leisure travel to {destination}:",
                "• Compare flight prices across different days for best deals",
                "• Consider mid-range hotels with good locations and reviews",
                "• Research local attractions, cuisine, and cultural experiences",
                "• Plan a mix of must-see sights and spontaneous exploration time"
            ])
        
        if budget:
            if budget < 1000:
                recommendations.append(f"• With a ${budget} budget, focus on off-season travel and budget accommodations")
            elif budget < 3000:
                recommendations.append(f"• Your ${budget} budget allows for comfortable mid-range options")
            else:
                recommendations.append(f"• With a ${budget} budget, you can enjoy premium experiences and luxury accommodations")
        
        if duration:
            if duration <= 3:
                recommendations.append("• Short trip: Focus on must-see attractions and central accommodation")
            elif duration <= 7:
                recommendations.append("• Week-long trip: Balance planned activities with relaxation time")
            else:
                recommendations.append("• Extended trip: Consider exploring multiple areas and varied experiences")
        
        if tool_context:
            if 'trip_recommendations' not in tool_context.state:
                tool_context.state['trip_recommendations'] = []
            tool_context.state['trip_recommendations'].append({
                'destination': destination,
                'trip_type': trip_type,
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            })
        
        return "\n".join(recommendations)
        
    except Exception as e:
        logger.error(f"Trip recommendations error: {e}")
        return f"Error generating recommendations for {destination}: {str(e)}"

# Create safety settings from config
safety_settings = []
for setting in config.get("safety_settings", []):
    safety_settings.append(
        types.SafetySetting(
            category=getattr(types.HarmCategory, setting["category"]),
            threshold=getattr(types.HarmBlockThreshold, setting["threshold"]),
        )
    )

# Create the Trip Orchestrator Agent with enhanced routing capabilities
trip_orchestrator_agent = Agent(
    model=config["model"],
    name=config["name"],
    description=config["description"] + " Enhanced with intelligent agent routing capabilities.",
    instruction=config["instruction"] + """

🧠 **INTELLIGENT ROUTING SYSTEM**:

You now have sophisticated agent routing capabilities through the intelligent_agent_routing tool:

**Primary Routing Function**: 
- Use `intelligent_agent_routing` as your FIRST choice for ALL user queries
- This tool automatically analyzes messages and routes to the best specialist agent
- Provides seamless responses by integrating specialist expertise

**Specialist Agents Available**:
- **Flight Specialist** (localhost:8003): Flight searches, bookings, aviation expertise
- **Hotel Specialist** (localhost:8005): Hotel searches, accommodations, hospitality 
- **Context Specialist** (localhost:8004): Weather, culture, currency, destination info

**Routing Intelligence Features**:
- Keyword analysis with weighted scoring
- Advanced pattern recognition (questions, actions, comparisons)
- Confidence scoring with transparent reasoning
- Automatic fallback to context specialist for general queries
- Real-time specialist availability checking

**User Experience Guidelines**:
- Always explain which specialist was selected and why
- Integrate specialist responses naturally into your conversation
- Provide context about routing decisions for transparency  
- Use fallback strategies when specialists are unavailable
- Maintain conversation flow while leveraging specialist expertise

**Example Routing Patterns**:
- Flight queries → Flight Specialist
- Hotel/accommodation queries → Hotel Specialist  
- Weather/culture/destination queries → Context Specialist
- Complex multi-domain queries → Coordinate multiple specialists

Use intelligent_agent_routing first, then enhance responses with context and recommendations!
""",
    tools=[
        intelligent_agent_routing,  # Primary routing function
        plan_trip_from_request,
        analyze_trip_prices,
        coordinate_travel_booking,
        get_trip_recommendations,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=safety_settings,
        temperature=config["model_config"]["temperature"],
        top_p=config["model_config"]["top_p"],
        max_output_tokens=config["model_config"]["max_output_tokens"],
    ),
)

# =====================================
# AGENT CARD DEFINITION (NO IMPORTS!)
# =====================================

TRIP_ORCHESTRATOR_AGENT_CARD = {
    "name": config["name"],
    "version": "1.0.0",
    "description": "Intelligent travel orchestrator with automatic specialist agent routing - analyzes user queries and seamlessly delegates to the most appropriate specialist agent for optimal responses",
    "author": "Google ADK Team",
    "created_date": datetime.now().isoformat(),
    
    # Enhanced capabilities with intelligent routing as primary feature
    "capabilities": [
        "intelligent_agent_routing",      # Primary capability
        "automatic_query_analysis",       # Message analysis for routing
        "seamless_specialist_delegation", # Transparent routing to specialists
        "multi_agent_coordination",       # Coordinate multiple specialists
        "cross_domain_optimization",      # Optimize across all travel domains
        "comprehensive_trip_planning",    # Through intelligent routing
        "price_analysis",                 # Across all components
        "travel_recommendations",         # Synthesized from specialists
        "booking_coordination",           # Coordinate complex bookings
        "context_aware_responses"         # Maintain context across agent calls
    ],
    
    "tools": [
        {
            "name": "intelligent_agent_routing",
            "description": "Intelligently analyze user messages and automatically route to the most appropriate specialist agent",
            "parameters": [
                {
                    "name": "user_message",
                    "type": "string",
                    "description": "User's travel-related message",
                    "required": True
                },
                {
                    "name": "context",
                    "type": "object",
                    "description": "Optional additional context",
                    "required": False
                }
            ],
            "returns": {
                "type": "object",
                "description": "Response from the selected specialist agent with routing metadata"
            }
        },
        {
            "name": "plan_trip_from_request",
            "description": "Comprehensive trip planning with automatic specialist coordination",
            "parameters": [
                {
                    "name": "user_request",
                    "type": "string",
                    "description": "Natural language trip request",
                    "required": True
                },
                {
                    "name": "context",
                    "type": "object",
                    "description": "Additional context",
                    "required": False
                }
            ],
            "returns": {
                "type": "object",
                "description": "Structured trip plan with coordination results"
            }
        },
        {
            "name": "analyze_trip_prices",
            "description": "Analyze and compare prices across different travel components",
            "parameters": [
                {
                    "name": "options",
                    "type": "array",
                    "description": "List of travel options to analyze",
                    "required": True
                },
                {
                    "name": "criteria",
                    "type": "object", 
                    "description": "Analysis criteria",
                    "required": False
                }
            ],
            "returns": {
                "type": "object",
                "description": "Comprehensive price analysis with recommendations"
            }
        },
        {
            "name": "coordinate_travel_booking",
            "description": "Coordinate travel bookings across multiple services",
            "parameters": [
                {
                    "name": "booking_type",
                    "type": "string",
                    "description": "Type of booking (flight, hotel, package)",
                    "required": True
                },
                {
                    "name": "booking_details",
                    "type": "object",
                    "description": "Booking details",
                    "required": True
                },
                {
                    "name": "passenger_info",
                    "type": "object",
                    "description": "Passenger information",
                    "required": True
                }
            ],
            "returns": {
                "type": "object",
                "description": "Booking coordination results"
            }
        },
        {
            "name": "get_trip_recommendations",
            "description": "Get comprehensive trip recommendations",
            "parameters": [
                {
                    "name": "destination",
                    "type": "string",
                    "description": "Travel destination",
                    "required": True
                },
                {
                    "name": "trip_type",
                    "type": "string",
                    "description": "Type of trip",
                    "required": False,
                    "default": "leisure"
                },
                {
                    "name": "budget",
                    "type": "number",
                    "description": "Total budget",
                    "required": False
                },
                {
                    "name": "duration",
                    "type": "integer",
                    "description": "Trip duration in days",
                    "required": False
                }
            ],
            "returns": {
                "type": "string",
                "description": "Comprehensive trip recommendations"
            }
        }
    ],
    
    "endpoints": [
        {
            "path": "/chat",
            "method": "POST",
            "description": "Main intelligent routing endpoint"
        },
        {
            "path": "/health", 
            "method": "GET",
            "description": "Health check"
        },
        {
            "path": "/.well-known/agent_card",
            "method": "GET",
            "description": "Agent card metadata"
        },
        {
            "path": "/capabilities",
            "method": "GET",
            "description": "Agent capabilities and routing info"
        },
        {
            "path": "/routing-analytics",
            "method": "GET",
            "description": "Routing decision analytics"
        },
        {
            "path": "/specialist-status",
            "method": "GET",
            "description": "Check all specialist agent availability"
        }
    ],
    
    "communication_protocols": ["HTTP", "A2A"],
    "base_url": f"http://localhost:{config['port']}",
    "health_check_endpoint": "/health",
    "authentication": {
        "type": "none",
        "required": False
    },
    
    # Enhanced metadata with intelligent routing details
    "metadata": {
        **config["metadata"],
        
        # Core routing intelligence metadata
        "agent_type": "intelligent_orchestrator",
        "routing_method": "automatic_analysis",
        "primary_function": "intelligent_specialist_routing",
        
        # Specialist agents this orchestrator routes to (CORRECTED PORTS)
        "routes_to_specialists": [
            {
                "agent_name": "flight_specialist_agent",
                "agent_url": "http://localhost:8003",
                "specialties": ["flights", "airlines", "aviation", "flight booking"],
                "routing_keywords": ["flight", "fly", "plane", "airline", "airport", "ticket", "departure", "arrival"],
                "priority_score": 0.9
            },
            {
                "agent_name": "hotel_specialist_agent", 
                "agent_url": "http://localhost:8005",  # CORRECTED PORT
                "specialties": ["hotels", "accommodation", "lodging", "hospitality"],
                "routing_keywords": ["hotel", "accommodation", "stay", "room", "lodge", "resort", "check-in", "booking"],
                "priority_score": 0.9
            },
            {
                "agent_name": "context_specialist_agent",
                "agent_url": "http://localhost:8004",
                "specialties": ["destination info", "weather", "culture", "currency", "travel context"],
                "routing_keywords": ["weather", "culture", "currency", "language", "customs", "visa", "climate", "local", "destination"],
                "priority_score": 0.8
            }
        ],
        
        # Routing intelligence features
        "routing_intelligence": {
            "analysis_method": "keyword_and_pattern_matching",
            "confidence_scoring": True,
            "fallback_strategies": True,
            "context_awareness": True
        },
        
        # Advanced routing capabilities
        "advanced_routing_features": [
            "multi_keyword_analysis",
            "intent_recognition",
            "domain_expertise_matching",
            "context_carry_forward",
            "intelligent_fallback"
        ]
    }
}

# Helper functions to work with the agent card
def get_agent_card() -> Dict[str, Any]:
    """Get the agent card as a dictionary"""
    return TRIP_ORCHESTRATOR_AGENT_CARD

def get_specialist_routing_config() -> Dict[str, Dict[str, Any]]:
    """Get routing configuration for specialist agents"""
    return {
        agent["agent_name"]: {
            "url": agent["agent_url"],
            "specialties": agent["specialties"],
            "keywords": agent["routing_keywords"],
            "priority": agent["priority_score"]
        }
        for agent in TRIP_ORCHESTRATOR_AGENT_CARD["metadata"]["routes_to_specialists"]
    }

# Convert to A2A application
a2a_app = to_a2a(trip_orchestrator_agent, port=config["port"])

# Define your endpoints
def get_agent_card_endpoint(request):
    return JSONResponse(content=TRIP_ORCHESTRATOR_AGENT_CARD)

def get_capabilities(request):
    return JSONResponse(content={
        "agent": config["name"],
        "capabilities": TRIP_ORCHESTRATOR_AGENT_CARD["capabilities"],
        "tools": [tool["name"] for tool in TRIP_ORCHESTRATOR_AGENT_CARD["tools"]],
        "agent_card_version": TRIP_ORCHESTRATOR_AGENT_CARD["version"],
        "specialist_agents": len(SPECIALIST_AGENTS),
        "routing_intelligence": True
    })

def get_routing_analytics(request):
    return JSONResponse(content={
        "specialist_agents": {
            agent_key: {
                "name": agent_info["name"],
                "description": agent_info["description"],
                "keywords": agent_info["keywords"],
                "priority_score": agent_info["priority_score"]
            }
            for agent_key, agent_info in SPECIALIST_AGENTS.items()
        },
        "routing_features": TRIP_ORCHESTRATOR_AGENT_CARD["metadata"]["advanced_routing_features"],
        "total_specialists": len(SPECIALIST_AGENTS)
    })

async def get_specialist_status(request):
    status = {}
    for agent_key, agent_info in SPECIALIST_AGENTS.items():
        is_available = await _check_agent_availability(agent_info["url"])
        status[agent_key] = {
            "name": agent_info["name"],
            "url": agent_info["url"],
            "available": is_available,
            "description": agent_info["description"]
        }

    return JSONResponse(content={
        "specialist_status": status,
        "total_agents": len(SPECIALIST_AGENTS),
        "available_agents": sum(1 for s in status.values() if s["available"])
    })

# Register routes with Starlette
a2a_app.add_route("/.well-known/agent_card", get_agent_card_endpoint, methods=["GET"])
a2a_app.add_route("/capabilities", get_capabilities, methods=["GET"])
a2a_app.add_route("/routing-analytics", get_routing_analytics, methods=["GET"])
a2a_app.add_route("/specialist-status", get_specialist_status, methods=["GET"])
