# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import yaml
from pathlib import Path

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from fastapi.responses import JSONResponse

# Import agent card
from .agent_card import get_agent_card

# Load configuration
def load_config():
    config_path = Path(__file__).parent / "agent_config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Convert to A2A application
a2a_app = to_a2a(context_specialist_agent, port=config["port"])

# Add agent card endpoint
@a2a_app.get("/.well-known/agent_card")
async def get_agent_card_endpoint():
    agent_card = get_agent_card()
    return JSONResponse(content=agent_card.dict())

@a2a_app.get("/capabilities")
async def get_capabilities():
    agent_card = get_agent_card()
    return {
        "agent": config["name"],
        "capabilities": agent_card.capabilities,
        "tools": [tool.name for tool in agent_card.tools],
        "aws_integration": config["metadata"]["aws_integration"]
    }

@a2a_app.get("/config")
async def get_config():
    """Get agent configuration (for debugging)"""
    return {
        "name": config["name"],
        "model": config["model"],
        "port": config["port"],
        "version": config["version"]
    }