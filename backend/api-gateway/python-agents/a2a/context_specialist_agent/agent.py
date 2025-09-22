# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import yaml
from pathlib import Path

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from fastapi import FastAPI # Import FastAPI
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute # Import APIRoute for custom routing

# Load configuration
def load_config():
    config_path = Path(__file__).parent / "agent_config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add to all A2A agents
class A2AResponseValidator:
    @staticmethod
    def validate_api_only_response(response: str, api_data: Dict[str, Any]) -> bool:
        """Ensure response contains only API data"""
        forbidden_phrases = [
            "typically", "usually", "generally", "often", "normally",
            "around", "about", "approximately", "roughly", "i estimate"
        ]
        
        for phrase in forbidden_phrases:
            if phrase in response.lower():
                logger.warning(f"A2A Response validation failed: contains '{phrase}'")
                return False
        
        # Check if response references API data
        if api_data and not any(str(value).lower() in response.lower() 
                              for value in api_data.values() if isinstance(value, (str, int, float))):
            logger.warning("A2A Response validation failed: no API data referenced")
            return False
        
        return True

# Context Tools for A2A Integration
async def get_weather_info(
    location: str,
    date: Optional[str] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Get weather information and travel recommendations for destinations
    
    Args:
        location: Destination city or airport code
        date: Optional travel date (YYYY-MM-DD)
        tool_context: Tool context for state management
        
    Returns:
        Weather information with travel recommendations
    """
    logger.info(f"Getting weather for {location} on {date or 'current'}")
    
    try:
        # Enhanced weather database with more destinations
        weather_database = {
            "PAR": {
                "forecast": "Mild temperatures, occasional rain. Perfect for walking tours.",
                "temperature": "15-20°C (59-68°F)",
                "season_tip": "Pack layers and waterproof jacket",
                "best_activities": ["museums", "cafes", "indoor attractions"],
                "travel_advice": "Spring and fall are ideal for visiting"
            },
            "LON": {
                "forecast": "Cool and rainy climate. Classic British weather.",
                "temperature": "10-18°C (50-64°F)", 
                "season_tip": "Umbrella essential, dress warmly",
                "best_activities": ["museums", "pubs", "theaters"],
                "travel_advice": "Summer has the longest days and warmest weather"
            },
            "NYC": {
                "forecast": "Four distinct seasons. Check current conditions.",
                "temperature": "Varies by season (-5°C to 30°C)",
                "season_tip": "Layer clothing, check forecast before travel",
                "best_activities": ["outdoor markets", "parks", "rooftop bars"],
                "travel_advice": "Spring and fall offer perfect weather"
            },
            "TYO": {
                "forecast": "Humid summers, cool winters. Cherry blossoms in spring.",
                "temperature": "5-30°C depending on season",
                "season_tip": "Check seasonal weather, pack accordingly",
                "best_activities": ["temples", "gardens", "street food"],
                "travel_advice": "Spring (cherry blossom) and fall are most popular"
            },
            "LAX": {
                "forecast": "Warm and sunny year-round. California dreaming weather.",
                "temperature": "18-25°C (64-77°F)",
                "season_tip": "Light clothing, sunscreen recommended", 
                "best_activities": ["beaches", "outdoor dining", "hiking"],
                "travel_advice": "Consistent weather makes any time good to visit"
            }
        }
        
        weather_info = weather_database.get(location.upper(), {
            "forecast": "Check local weather forecast before traveling",
            "temperature": "Variable",
            "season_tip": "Research seasonal conditions for your destination",
            "best_activities": ["local attractions", "cultural sites"],
            "travel_advice": "Research the best time to visit your destination"
        })
        
        # Store in tool context
        if tool_context:
            if 'weather_queries' not in tool_context.state:
                tool_context.state['weather_queries'] = []
            tool_context.state['weather_queries'].append({
                'location': location,
                'date': date,
                'timestamp': datetime.now().isoformat()
            })
        
        return {
            "location": location,
            "date": date or "current",
            "forecast": weather_info["forecast"],
            "temperature": weather_info["temperature"],
            "recommendations": {
                "packing": weather_info["season_tip"],
                "activities": weather_info["best_activities"],
                "travel_timing": weather_info["travel_advice"]
            },
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Weather tool error: {e}")
        return {
            "location": location,
            "status": "error", 
            "message": f"Weather lookup failed: {str(e)}"
        }

async def get_currency_info(
    destination: str,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Get currency information, exchange rates, and payment tips
    
    Args:
        destination: Destination country or city code
        tool_context: Tool context for state management
        
    Returns:
        Currency and payment information
    """
    logger.info(f"Getting currency info for {destination}")
    
    try:
        currency_database = {
            "PAR": {
                "currency": "Euro (EUR)",
                "symbol": "€",
                "exchange_rate": "1 USD ≈ 0.92 EUR",
                "payment_methods": ["Credit cards widely accepted", "Contactless payments", "Cash for small vendors"],
                "atm_info": "ATMs abundant, small fees apply",
                "tipping": "5-10% at restaurants, round up for taxis",
                "budget_tips": ["Lunch menus cheaper than dinner", "Happy hour 4-7pm", "Museum passes save money"]
            },
            "LON": {
                "currency": "British Pound (GBP)",
                "symbol": "£",
                "exchange_rate": "1 USD ≈ 0.79 GBP", 
                "payment_methods": ["Contactless everywhere", "Chip & PIN standard", "Mobile payments popular"],
                "atm_info": "ATMs everywhere, check foreign transaction fees",
                "tipping": "10-15% at restaurants, not required at pubs",
                "budget_tips": ["Pub lunches cheaper", "Off-peak transport rates", "Free museums"]
            },
            "TYO": {
                "currency": "Japanese Yen (JPY)",
                "symbol": "¥",
                "exchange_rate": "1 USD ≈ 150 JPY",
                "payment_methods": ["Cash preferred", "IC cards for transport", "Credit cards at major stores"],
                "atm_info": "7-Eleven ATMs accept foreign cards",
                "tipping": "No tipping culture - can be offensive",
                "budget_tips": ["Convenience store meals", "Business lunch sets", "Free temple visits"]
            },
            "NYC": {
                "currency": "US Dollar (USD)",
                "symbol": "$",
                "exchange_rate": "Base currency",
                "payment_methods": ["Cards accepted everywhere", "Mobile payments common", "Cash backup recommended"],
                "atm_info": "ATMs everywhere",
                "tipping": "18-20% restaurants, $1-2 per drink",
                "budget_tips": ["Food trucks cheaper", "Happy hour specials", "Free Staten Island Ferry"]
            }
        }
        
        currency_info = currency_database.get(destination.upper(), {
            "currency": "Local currency",
            "symbol": "¤",
            "exchange_rate": "Check current rates",
            "payment_methods": ["Research local payment preferences"],
            "atm_info": "Check ATM network compatibility",
            "tipping": "Research local tipping customs",
            "budget_tips": ["Research local money-saving tips"]
        })
        
        # Store in tool context
        if tool_context:
            if 'currency_queries' not in tool_context.state:
                tool_context.state['currency_queries'] = []
            tool_context.state['currency_queries'].append({
                'destination': destination,
                'timestamp': datetime.now().isoformat()
            })
        
        return {
            "destination": destination,
            "currency_details": currency_info,
            "last_updated": "2025-01-15",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Currency tool error: {e}")
        return {
            "destination": destination,
            "status": "error",
            "message": f"Currency lookup failed: {str(e)}"
        }

async def get_cultural_insights(
    destination: str,
    trip_type: str = "leisure",
    tool_context: ToolContext = None
) -> str:
    """Get cultural insights, etiquette tips, and local customs
    
    Args:
        destination: Destination country or city
        trip_type: Type of trip (leisure, business, romantic, family)
        tool_context: Tool context for state management
        
    Returns:
        Cultural insights formatted as string
    """
    logger.info(f"Getting cultural tips for {destination} ({trip_type} trip)")
    
    try:
        cultural_database = {
            "PAR": {
                "greeting": "Always say 'Bonjour/Bonsoir' before asking questions",
                "dining": "Lunch 12-2pm, Dinner after 7:30pm. Savor your meals",
                "etiquette": "Dress elegantly for restaurants. Many shops close Sunday",
                "language": "Learn: 'Merci', 'S'il vous plaît', 'Excusez-moi', 'Parlez-vous anglais?'",
                "do_nots": ["Don't eat on public transport", "Don't speak loudly", "Don't wear flip-flops to dinner"],
                "customs": "French value politeness and proper greetings above all"
            },
            "LON": {
                "greeting": "Queue politely, 'mind the gap' on tube, weather chat is normal",
                "dining": "Pub culture essential. Sunday roast is traditional. Tea at 4pm",
                "etiquette": "Apologize frequently, even when not at fault",
                "language": "British terms: lift (elevator), loo (bathroom), queue (line), brilliant (great)",
                "do_nots": ["Never jump queues", "Don't talk loudly on transport", "Don't criticize the Royal Family"],
                "customs": "Understatement is valued, direct compliments can seem insincere"
            },
            "TYO": {
                "greeting": "Slight bow when meeting. Remove shoes when entering homes",
                "dining": "Slurping ramen shows appreciation. Never tip - it's offensive",
                "etiquette": "Be quiet on trains. Don't eat while walking. Bow slightly",
                "language": "'Arigato gozaimasu', 'Sumimasen', 'Konnichiwa', 'Hai'",
                "do_nots": ["Don't blow nose in public", "Don't point with one finger", "Don't wear shoes indoors"],
                "customs": "Group harmony (wa) is paramount. Individual needs come second"
            }
        }
        
        base_info = cultural_database.get(destination.upper(), {
            "greeting": "Research local greeting customs and social norms",
            "dining": "Learn about local dining etiquette and meal times", 
            "etiquette": "Respect local customs, dress codes, and social expectations",
            "language": "Learn basic phrases: hello, thank you, excuse me, help",
            "do_nots": ["Research cultural taboos and sensitive topics"],
            "customs": "Observe local behavior and follow social cues"
        })
        
        # Trip-specific additions
        trip_advice = ""
        if trip_type.lower() == "romantic":
            trip_advice = f"\nRomantic Tip: In {destination}, research romantic restaurants, sunset viewpoints, and couples' activities. Evening strolls and intimate dining are usually appreciated."
        elif trip_type.lower() == "business":
            trip_advice = f"\nBusiness Tip: For {destination}, learn business card etiquette, meeting protocols, appropriate dress codes, and punctuality expectations."
        elif trip_type.lower() == "family":
            trip_advice = f"\nFamily Tip: In {destination}, find family-friendly areas, child discounts, kid-safe zones, and activities suitable for different ages."
        
        # Format as readable string
        cultural_guide = f"""Cultural Guide for {destination}:

🤝 Greeting: {base_info['greeting']}
🍽️ Dining: {base_info['dining']}  
✨ Etiquette: {base_info['etiquette']}
🗣️ Language: {base_info['language']}
❌ Avoid: {', '.join(base_info['do_nots'])}
🏛️ Customs: {base_info['customs']}{trip_advice}"""
        
        # Store in tool context
        if tool_context:
            if 'cultural_queries' not in tool_context.state:
                tool_context.state['cultural_queries'] = []
            tool_context.state['cultural_queries'].append({
                'destination': destination,
                'trip_type': trip_type,
                'timestamp': datetime.now().isoformat()
            })
        
        return cultural_guide
        
    except Exception as e:
        logger.error(f"Cultural tips tool error: {e}")
        return f"Error getting cultural information for {destination}: {str(e)}"

async def get_comprehensive_travel_context(
    destination: str,
    trip_type: str = "leisure",
    travel_date: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Get complete travel context combining weather, currency, and cultural information
    
    Args:
        destination: Travel destination
        trip_type: Type of trip
        travel_date: Optional travel date
        tool_context: Tool context for state management
        
    Returns:
        Comprehensive travel context as formatted string
    """
    logger.info(f"Getting comprehensive context for {destination}")
    
    try:
        # Get all information in parallel
        weather_task = get_weather_info(destination, travel_date, tool_context)
        currency_task = get_currency_info(destination, tool_context)
        cultural_task = get_cultural_insights(destination, trip_type, tool_context)
        
        weather_info, currency_info, cultural_info = await asyncio.gather(
            weather_task, currency_task, cultural_task
        )
        
        # Format comprehensive response
        context_summary = f"""🌍 Complete Travel Context for {destination}

☀️ WEATHER & CLIMATE:
{weather_info.get('forecast', 'Weather information unavailable')}
Temperature: {weather_info.get('temperature', 'Variable')}
Packing: {weather_info.get('recommendations', {}).get('packing', 'Check local conditions')}

💰 CURRENCY & PAYMENTS:
Currency: {currency_info.get('currency_details', {}).get('currency', 'Local currency')}
Payment: {', '.join(currency_info.get('currency_details', {}).get('payment_methods', ['Research local methods']))}
Tipping: {currency_info.get('currency_details', {}).get('tipping', 'Research local customs')}

{cultural_info}

🎯 Trip Type: {trip_type.title()}
📅 Travel Date: {travel_date or 'Not specified'}
"""
        
        return context_summary
        
    except Exception as e:
        logger.error(f"Comprehensive context error: {e}")
        return f"Error compiling travel context for {destination}: {str(e)}"
    
safety_settings = []
for setting in config.get("safety_settings", []):
    safety_settings.append(
        types.SafetySetting(
            category=getattr(types.HarmCategory, setting["category"]),
            threshold=getattr(types.HarmBlockThreshold, setting["threshold"]),
        )
    )

# Create the agent using configuration
context_specialist_agent = Agent(
    model=config["model"],
    name=config["name"],
    description=config["description"],
    instruction=config["instruction"],
    tools=[
        get_weather_info,
        get_currency_info,
        get_cultural_insights,
        get_comprehensive_travel_context,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=safety_settings,
        temperature=config["model_config"]["temperature"],
        top_p=config["model_config"]["top_p"],
        max_output_tokens=config["model_config"]["max_output_tokens"],
    ),
)

# =====================================
# CREATE FASTAPI APP DIRECTLY (BYPASS to_a2a)
# =====================================

# Create FastAPI app directly instead of using problematic to_a2a
a2a_app = FastAPI(
    title="Context Specialist Agent", 
    version="1.0.0",
    description="Expert travel context specialist providing weather forecasts, currency information, and cultural insights"
)

@a2a_app.post("/chat")
async def chat_endpoint(request: dict):
    """Main chat endpoint that integrates with Google ADK Agent"""
    try:
        message = request.get("message", "")
        context = request.get("context", {})
        
        if not message:
            return {"error": "No message provided"}
        
        logger.info(f"Processing chat message: {message}")
        
        # Enhanced message parsing and tool routing
        message_lower = message.lower()
        
        # Parse parameters from message (simplified for example)
        def extract_location(msg: str) -> str:
            common_cities = {
                "paris": "PAR", "london": "LON", "new york": "NYC", "tokyo": "TYO",
                "los angeles": "LAX", "rome": "ROM", "berlin": "BER", "sydney": "SYD"
            }
            for city, code in common_cities.items():
                if city in msg.lower():
                    return code
            return "PAR"  # Default
        
        def extract_date(msg: str) -> Optional[str]:
            # Simple date extraction - enhance for real parsing
            if "on " in msg: return msg.split("on ")[1].split(" ")[0]
            if "in " in msg and len(msg.split("in ")[1].split(" ")[0]) == 4: # e.g., "in 2025"
                return msg.split("in ")[1].split(" ")[0]
            return None
        
        def extract_trip_type(msg: str) -> str:
            if any(word in msg for word in ["romantic", "honeymoon"]): return "romantic"
            if any(word in msg for word in ["business", "work"]): return "business"
            if any(word in msg for word in ["family", "kids"]): return "family"
            return "leisure"
        
        # Route to appropriate tool based on message intent
        if any(word in message_lower for word in ["weather", "climate", "forecast", "temperature"]):
            location = extract_location(message)
            date = extract_date(message)
            result = await get_weather_info(location, date)
            return {
                "message": f"Here's the weather information for {location}:",
                "data": result,
                "suggestions": ["What about currency?", "Tell me about local customs."]
            }
        
        elif any(word in message_lower for word in ["currency", "money", "exchange", "tipping", "payment"]):
            location = extract_location(message)
            result = await get_currency_info(location)
            return {
                "message": f"Here's currency information for {location}:",
                "data": result,
                "suggestions": ["What about weather?", "Tell me about local customs."]
            }
        
        elif any(word in message_lower for word in ["culture", "customs", "etiquette", "language", "traditions"]):
            location = extract_location(message)
            trip_type = extract_trip_type(message)
            result = await get_cultural_insights(location, trip_type)
            return {
                "message": f"Here are some cultural insights for {location}:",
                "data": result,
                "suggestions": ["What about weather?", "Tell me about currency."]
            }
        
        elif any(word in message_lower for word in ["comprehensive", "full context", "all info", "complete guide"]):
            location = extract_location(message)
            trip_type = extract_trip_type(message)
            date = extract_date(message)
            result = await get_comprehensive_travel_context(location, trip_type, date)
            return {
                "message": f"Here's a comprehensive travel guide for {location}:",
                "data": result,
                "suggestions": ["Anything else I can help with?"]
            }
        
        elif any(word in message_lower for word in ["help", "what", "how", "can you"]):
            return {
                "message": "I'm your Context Specialist! Here's what I can help you with:",
                "capabilities": [
                    "☀️ **Weather & Climate**: Get forecasts, seasonal advice, and packing recommendations.",
                    "💰 **Currency & Finance**: Learn about exchange rates, payment methods, and tipping customs.",
                    "🏛️ **Cultural Insights**: Understand local etiquette, customs, and language tips.",
                    "🌍 **Comprehensive Context**: Get a full travel briefing combining all information."
                ],
                "examples": [
                    "What's the weather like in Paris in March?",
                    "What currency do they use in Tokyo?",
                    "Tell me about the culture in London for a business trip.",
                    "Give me a comprehensive guide for New York."
                ]
            }
        
        else:
            return {
                "message": "I'm your Context Specialist! I can provide weather, currency, and cultural information for your travel destinations.",
                "guidance": "Try asking me about:",
                "suggestions": [
                    "Weather in [city]",
                    "Currency in [city]",
                    "Culture in [city]",
                    "A comprehensive guide for [city]"
                ],
                "specializations": ["Weather", "Currency", "Culture", "Travel Context"]
            }
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return {
            "error": "I encountered an issue processing your request.",
            "message": "Please try rephrasing your question or ask me about weather, currency, or culture.",
            "debug": str(e) if os.getenv("DEBUG") == "true" else None
        }

@a2a_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "agent": config["name"],
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "capabilities": ["weather", "currency", "culture", "comprehensive_context"]
    }

@a2a_app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """Agent card endpoint for A2A discovery"""
    return JSONResponse(content={
        "name": config["name"],
        "version": "1.0.0",
        "description": config["description"],
        "author": "Google ADK Team",
        "created_date": datetime.now().isoformat(),
        "capabilities": [
            "weather_forecasting",
            "currency_information",
            "cultural_insights",
            "travel_context",
            "destination_guidance",
            "etiquette_advice"
        ],
        "tools": [
            {
                "name": "get_weather_info",
                "description": "Get weather information and travel recommendations",
                "parameters": [
                    {"name": "location", "type": "string", "description": "Destination location", "required": True},
                    {"name": "date", "type": "string", "description": "Travel date (YYYY-MM-DD)", "required": False}
                ],
                "returns": {"type": "object", "description": "Weather forecast and travel advice"}
            },
            {
                "name": "get_currency_info", 
                "description": "Get currency and payment information",
                "parameters": [
                    {"name": "destination", "type": "string", "description": "Destination country/city", "required": True}
                ],
                "returns": {"type": "object", "description": "Currency details and payment methods"}
            },
            {
                "name": "get_cultural_insights",
                "description": "Get cultural insights and etiquette tips",
                "parameters": [
                    {"name": "destination", "type": "string", "description": "Destination location", "required": True},
                    {"name": "trip_type", "type": "string", "description": "Type of trip", "required": False, "enum": ["leisure", "business", "romantic", "family"]}
                ],
                "returns": {"type": "string", "description": "Cultural guide and etiquette tips"}
            },
            {
                "name": "get_comprehensive_travel_context",
                "description": "Get complete travel context combining weather, currency, and cultural information",
                "parameters": [
                    {"name": "destination", "type": "string", "description": "Travel destination", "required": True},
                    {"name": "trip_type", "type": "string", "description": "Type of trip", "required": False, "enum": ["leisure", "business", "romantic", "family"]},
                    {"name": "travel_date", "type": "string", "description": "Travel date (YYYY-MM-DD)", "required": False}
                ],
                "returns": {"type": "string", "description": "Comprehensive travel context summary"}
            }
        ],
        "endpoints": [
            {"path": "/chat", "method": "POST", "description": "Main chat endpoint"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/.well-known/agent_card", "method": "GET", "description": "Agent card metadata"}
        ],
        "communication_protocols": ["HTTP", "A2A"],
        "base_url": f"http://localhost:{config['port']}",
        "health_check_endpoint": "/health",
        "authentication": {
            "type": "none",
            "required": False
        },
        "metadata": {
            "model": "gemini-2.0-flash",
            "specializations": ["weather", "currency", "culture", "travel_planning", "destination_expertise"],
            "coverage": "global"
        }
    })

@a2a_app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities"""
    return {
        "agent": config["name"],
        "tools": ["get_weather_info", "get_currency_info", "get_cultural_insights", "get_comprehensive_travel_context"],
        "version": "1.0.0",
        "supported_features": [
            "weather_forecasts",
            "currency_exchange_rates",
            "cultural_etiquette",
            "comprehensive_travel_guides"
        ]
    }

@a2a_app.get("/info")
async def get_info():
    """Get basic agent information"""
    return {
        "agent_name": config["name"],
        "description": config["description"],
        "version": "1.0.0",
        "port": config["port"]
    }

# For running the server directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(a2a_app, host="0.0.0.0", port=config["port"])
