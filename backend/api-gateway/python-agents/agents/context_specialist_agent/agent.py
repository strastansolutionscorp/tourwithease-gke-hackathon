#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Specialist Agent for TourWithEase ADK System
Provides weather, currency, and cultural travel information
"""

import asyncio
import logging
from typing import Dict, Any, Optional
# Assuming base_agent.py contains the definitions for ADKAgent, Memory, A2AMessage, Tool
from base_agent import ADKAgent, Memory, A2AMessage, Tool

# Configure logging for development visibility
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('context_agent.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class WeatherTool(Tool):
    """Enhanced weather information tool"""
    
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get weather information and travel recommendations for destinations"
        )
        logger.debug("WeatherTool initialized.")

    async def execute(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
        """Get weather forecast and travel advice for location"""
        logger.debug(f"Executing WeatherTool with location: {location}, date: {date}")
        try:
            logger.info(f"Getting weather for {location} on {date or 'current'}")
            
            weather_database = {
                "PAR": {
                    "forecast": "Mild temperatures, occasional rain. Perfect for walking tours.",
                    "temperature": "15-20°C (59-68°F)",
                    "season_tip": "Pack layers and waterproof jacket",
                    "best_activities": ["museums", "cafes", "indoor attractions"]
                },
                "LON": {
                    "forecast": "Cool and rainy climate. Classic British weather.",
                    "temperature": "10-18°C (50-64°F)", 
                    "season_tip": "Umbrella essential, dress warmly",
                    "best_activities": ["museums", "pubs", "theaters"]
                },
                "NYC": {
                    "forecast": "Four distinct seasons. Check current conditions.",
                    "temperature": "Varies by season",
                    "season_tip": "Layer clothing, check forecast before travel",
                    "best_activities": ["outdoor markets", "parks", "rooftop bars"]
                },
                "LAX": {
                    "forecast": "Warm and sunny year-round. California dreaming weather.",
                    "temperature": "18-25°C (64-77°F)",
                    "season_tip": "Light clothing, sunscreen recommended", 
                    "best_activities": ["beaches", "outdoor dining", "hiking"]
                },
                "TYO": {
                    "forecast": "Humid summers, cool winters. Cherry blossoms in spring.",
                    "temperature": "Varies by season",
                    "season_tip": "Check seasonal weather, pack accordingly",
                    "best_activities": ["temples", "gardens", "street food"]
                }
            }
            
            weather_info = weather_database.get(location.upper(), {
                "forecast": "Check local weather forecast before traveling",
                "temperature": "Variable",
                "season_tip": "Research seasonal conditions",
                "best_activities": ["local attractions"]
            })
            logger.debug(f"Retrieved weather info for {location}: {weather_info}")
            
            result = {
                "status": "success",
                "location": location,
                "weather_data": weather_info,
                "source": "weather_service",
                "timestamp": date or "current"
            }
            logger.debug(f"WeatherTool execution successful. Returning: {result}")
            return result
            
        except Exception as e:
            logger.error(f"WeatherTool error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Weather lookup failed: {str(e)}",
                "location": location
            }

class CurrencyTool(Tool):
    """Enhanced currency and payment information tool"""
    
    def __init__(self):
        super().__init__(
            name="currency",
            description="Get currency information, exchange rates, and payment tips"
        )
        logger.debug("CurrencyTool initialized.")

    async def execute(self, destination: str) -> Dict[str, Any]:
        """Get comprehensive currency and payment information"""
        logger.debug(f"Executing CurrencyTool with destination: {destination}")
        try:
            logger.info(f"Getting currency info for {destination}")
            
            currency_database = {
                "PAR": {
                    "currency": "Euro (EUR)",
                    "symbol": "€",
                    "payment_tip": "Cards widely accepted. Small vendors may prefer cash.",
                    "exchange_rate": "1 USD ≈ 0.92 EUR",
                    "atm_availability": "Abundant, small fees",
                    "tipping_culture": "5-10% at restaurants, round up for taxis"
                },
                "LON": {
                    "currency": "British Pound (GBP)",
                    "symbol": "£",
                    "payment_tip": "Contactless payments everywhere. Pound is strong currency.",
                    "exchange_rate": "1 USD ≈ 0.79 GBP", 
                    "atm_availability": "Everywhere, check foreign fees",
                    "tipping_culture": "10-15% at restaurants, not required for pubs"
                },
                "TYO": {
                    "currency": "Japanese Yen (JPY)",
                    "symbol": "¥",
                    "payment_tip": "Cash still king! Get yen from 7-Eleven ATMs.",
                    "exchange_rate": "1 USD ≈ 150 JPY",
                    "atm_availability": "Convenience stores, not all accept foreign cards",
                    "tipping_culture": "No tipping - it can be offensive!"
                },
                "NYC": {
                    "currency": "US Dollar (USD)",
                    "symbol": "$",
                    "payment_tip": "Cards accepted everywhere. Mobile payments common.",
                    "exchange_rate": "Base currency",
                    "atm_availability": "Everywhere",
                    "tipping_culture": "18-20% at restaurants, $1-2 per drink at bars"
                }
            }
            
            currency_info = currency_database.get(destination.upper(), {
                "currency": "Local currency",
                "payment_tip": "Research local payment methods and currency",
                "exchange_rate": "Check current rates",
                "atm_availability": "Varies",
                "tipping_culture": "Research local customs"
            })
            logger.debug(f"Retrieved currency info for {destination}: {currency_info}")
            
            result = {
                "status": "success",
                "destination": destination,
                "currency_info": currency_info,
                "last_updated": "2025-09-18"
            }
            logger.debug(f"CurrencyTool execution successful. Returning: {result}")
            return result
            
        except Exception as e:
            logger.error(f"CurrencyTool error: {e}", exc_info=True)
            return {
                "status": "error", 
                "message": f"Currency lookup failed: {str(e)}",
                "destination": destination
            }

class CulturalTipsTool(Tool):
    """Enhanced cultural insights and etiquette tool"""
    
    def __init__(self):
        super().__init__(
            name="cultural_tips",
            description="Get cultural insights, etiquette tips, and local customs"
        )
        logger.debug("CulturalTipsTool initialized.")

    async def execute(self, destination: str, trip_type: str = "leisure") -> Dict[str, Any]:
        """Get comprehensive cultural information and tips"""
        logger.debug(f"Executing CulturalTipsTool with destination: {destination}, trip_type: {trip_type}")
        try:
            logger.info(f"Getting cultural tips for {destination} ({trip_type} trip)")
            
            cultural_database = {
                "PAR": {
                    "greeting": "Always say 'Bonjour/Bonsoir' before asking questions",
                    "dining": "Lunch 12-2pm, Dinner after 7:30pm. Long meals are cultural",
                    "etiquette": "Dress well for restaurants. Many shops close Sunday/Monday",
                    "language": "Learn 'Merci', 'S'il vous plaît', 'Excusez-moi'",
                    "do_nots": ["Don't eat on the metro", "Don't speak loudly in public"],
                    "local_customs": "Parisians value politeness and proper greetings"
                },
                "LON": {
                    "greeting": "Queue politely, 'mind the gap' on tube",
                    "dining": "Pub culture important. Sunday roast is traditional",
                    "etiquette": "Weather chat is common conversation starter",
                    "language": "British spellings: lift, loo, queue, brilliant",
                    "do_nots": ["Don't jump queues", "Don't talk loudly on transport"],
                    "local_customs": "Tea time is sacred, apologize frequently"
                },
                "TYO": {
                    "greeting": "Slight bow when meeting. Remove shoes indoors",
                    "dining": "Slurping ramen shows appreciation. No tipping!",
                    "etiquette": "Be quiet on trains. Don't eat while walking",
                    "language": "'Arigato gozaimasu', 'Sumimasen', 'Konnichiwa'",
                    "do_nots": ["Don't blow nose in public", "Don't point with fingers"],
                    "local_customs": "Group harmony is important, be respectful"
                }
            }
            
            base_info = cultural_database.get(destination.upper(), {
                "greeting": "Research local greeting customs",
                "dining": "Learn about local dining etiquette", 
                "etiquette": "Respect local customs and traditions",
                "language": "Learn basic phrases in local language",
                "do_nots": ["Research cultural taboos"],
                "local_customs": "Observe and follow local behavior"
            }).copy()
            logger.debug(f"Retrieved base cultural info for {destination}: {base_info}")
            
            # Add trip-specific advice
            if trip_type.lower() == "romantic":
                base_info["romantic_tip"] = "Research romantic restaurants, sunset spots, and couples activities"
                logger.debug("Added romantic trip tip.")
            elif trip_type.lower() == "business":
                base_info["business_tip"] = "Learn business card etiquette, meeting customs, and dress codes"
                logger.debug("Added business trip tip.")
            elif trip_type.lower() == "family":
                base_info["family_tip"] = "Find family-friendly activities, kid-safe areas, and child discounts"
                logger.debug("Added family trip tip.")
            
            result = {
                "status": "success",
                "destination": destination,
                "trip_type": trip_type,
                "cultural_info": base_info
            }
            logger.debug(f"CulturalTipsTool execution successful. Returning: {result}")
            return result
            
        except Exception as e:
            logger.error(f"CulturalTipsTool error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Cultural tips lookup failed: {str(e)}",
                "destination": destination
            }

class ContextSpecialist(ADKAgent):
    """
    Advanced Context Specialist Agent for comprehensive travel information
    Integrates weather, currency, and cultural data for travel planning
    """
    
    def __init__(self):
        logger.debug("Initializing ContextSpecialist agent...")
        tools = [
            WeatherTool(),
            CurrencyTool(), 
            CulturalTipsTool()
        ]
        logger.debug(f"Registered tools: {[tool.name for tool in tools]}")
        
        # FIX: Removed the unexpected 'model' keyword argument.
        # The ADKAgent base class does not accept 'model' in its constructor.
        # This was the cause of the initialization error.
        super().__init__(
            name="context-specialist",
            description="Expert travel context provider with weather, currency, and cultural insights",
            tools=tools,
            memory=Memory(memory_type="conversation_buffer", k=15)
        )
        
        # IMPROVEMENT: Switched from print() to logger.info() for consistent logging.
        logger.info("Context Specialist Agent initialized successfully")
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process travel context requests with comprehensive error handling"""
        logger.debug(f"Entering process_request with request: {request}")
        try:
            if isinstance(request, bytes):
                logger.debug("Request is in bytes, decoding to utf-8...")
                request = request.decode('utf-8', errors='replace')
                logger.warning("Converted bytes request to string")
            
            action = request.get("action", "get_travel_context")
            params = request.get("parameters", {})
            logger.debug(f"Extracted action: '{action}', parameters: {params}")
            
            handlers = {
                "get_travel_context": self._get_comprehensive_context,
                "get_weather": self._get_weather_only,
                "get_currency": self._get_currency_only,
                "get_cultural_tips": self._get_cultural_only
            }
            
            handler = handlers.get(action)
            if not handler:
                available_actions = list(handlers.keys())
                logger.warning(f"Unknown action '{action}', available: {available_actions}")
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "available_actions": available_actions
                }
            
            logger.debug(f"Routing to handler: {handler.__name__}")
            result = await handler(params)
            logger.info(f"Request processed successfully: {action}")
            logger.debug(f"Returning result from process_request: {result}")
            return result
            
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error: {e}", exc_info=True)
            return {
                "status": "error",
                "message": "Text encoding error - please ensure UTF-8 encoding",
                "error_type": "encoding_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error in process_request: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}",
                "error_type": "processing_error"
            }

    async def process_a2a_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle agent-to-agent requests"""
        logger.debug(f"Entering process_a2a_request from agent '{message.from_agent}' with payload: {message.payload}")
        logger.info(f"A2A request from {message.from_agent}: {message.payload}")
        result = await self.process_request(message.payload)
        logger.debug(f"Returning result from process_a2a_request: {result}")
        return result

    async def _get_comprehensive_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete travel context from all tools"""
        logger.debug(f"Entering _get_comprehensive_context with params: {params}")
        try:
            destination = params.get("destination")
            if not destination:
                logger.warning("Destination parameter is missing.")
                return {
                    "status": "error",
                    "message": "Destination parameter required",
                    "required_params": ["destination"]
                }
            
            trip_type = params.get("trip_type", "leisure") 
            travel_date = params.get("travel_date")
            logger.debug(f"Context parameters: destination='{destination}', trip_type='{trip_type}', travel_date='{travel_date}'")
            
            logger.info(f"Getting comprehensive context for {destination}")
            
            logger.debug("Creating parallel tasks for weather, currency, and cultural_tips tools.")
            tasks = [
                self.use_tool("weather", location=destination, date=travel_date),
                self.use_tool("currency", destination=destination),
                self.use_tool("cultural_tips", destination=destination, trip_type=trip_type)
            ]
            
            logger.debug("Executing tool tasks with asyncio.gather...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            logger.debug(f"Tool execution results (or exceptions): {results}")
            
            context = {
                "status": "success",
                "destination": destination,
                "trip_type": trip_type,
                "requested_date": travel_date
            }
            
            # Process results, checking for exceptions
            if isinstance(results[0], dict) and results[0].get("status") == "success":
                context["weather"] = results[0]["weather_data"]
                logger.debug("Successfully processed weather tool result.")
            else:
                logger.error(f"Weather tool failed: {results[0]}")
                context["weather_error"] = str(results[0])
            
            if isinstance(results[1], dict) and results[1].get("status") == "success":
                context["currency"] = results[1]["currency_info"]
                logger.debug("Successfully processed currency tool result.")
            else:
                logger.error(f"Currency tool failed: {results[1]}")
                context["currency_error"] = str(results[1])
            
            if isinstance(results[2], dict) and results[2].get("status") == "success":
                context["cultural_tips"] = results[2]["cultural_info"]
                logger.debug("Successfully processed cultural tips tool result.")
            else:
                logger.error(f"Cultural tool failed: {results[2]}")
                context["cultural_error"] = str(results[2])
            
            logger.debug("Generating context summary...")
            context["summary"] = self._generate_context_summary(context)
            logger.debug(f"Generated summary: {context['summary']}")
            
            memory_message = f"Provided comprehensive context for {destination}"
            self.memory.add_message("system", memory_message)
            logger.debug(f"Added to memory: '{memory_message}'")
            
            logger.debug(f"Returning comprehensive context: {context}")
            return context
            
        except Exception as e:
            logger.error(f"Error getting comprehensive context: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Failed to get travel context: {str(e)}"
            }

    def _generate_context_summary(self, context: Dict[str, Any]) -> str:
        """Create a readable summary of all context information"""
        logger.debug(f"Entering _generate_context_summary with context keys: {context.keys()}")
        summary_parts = []
        
        if "weather" in context and "forecast" in context["weather"]:
            summary_parts.append(f"Weather: {context['weather']['forecast']}")
        
        if "currency" in context and "payment_tip" in context["currency"]:
            summary_parts.append(f"Payment: {context['currency']['payment_tip']}")
        
        if "cultural_tips" in context and "greeting" in context["cultural_tips"]:
            summary_parts.append(f"Culture: {context['cultural_tips']['greeting']}")
        
        logger.debug(f"Generated summary parts: {summary_parts}")
        summary = " | ".join(summary_parts) if summary_parts else "Travel context information compiled"
        logger.debug(f"Final summary string: '{summary}'")
        return summary

    async def _get_weather_only(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get only weather information"""
        logger.debug(f"Entering _get_weather_only with params: {params}")
        location = params.get("location") or params.get("destination")
        date = params.get("date")
        if not location:
            return {"status": "error", "message": "Location or destination parameter required."}
        logger.debug(f"Calling 'weather' tool for location: {location}, date: {date}")
        return await self.use_tool("weather", location=location, date=date)

    async def _get_currency_only(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get only currency information"""
        logger.debug(f"Entering _get_currency_only with params: {params}")
        destination = params.get("destination")
        if not destination:
            return {"status": "error", "message": "Destination parameter required."}
        logger.debug(f"Calling 'currency' tool for destination: {destination}")
        return await self.use_tool("currency", destination=destination)

    async def _get_cultural_only(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get only cultural information"""
        logger.debug(f"Entering _get_cultural_only with params: {params}")
        destination = params.get("destination")
        if not destination:
            return {"status": "error", "message": "Destination parameter required."}
        trip_type = params.get("trip_type", "leisure")
        logger.debug(f"Calling 'cultural_tips' tool for destination: {destination}, trip_type: {trip_type}")
        return await self.use_tool("cultural_tips", destination=destination, trip_type=trip_type)

# Export the agent for ADK discovery
root_agent = ContextSpecialist()

if __name__ == "__main__":
    import json
    
    async def test_agent():
        """Test the agent functionality"""
        print("ðŸ§ª Testing Context Specialist Agent")
        logger.debug("Starting local agent test...")
        
        test_request = {
            "action": "get_travel_context",
            "parameters": {
                "destination": "PAR",
                "trip_type": "romantic",
                "travel_date": "2025-12-01"
            }
        }
        logger.debug(f"Test request payload: {json.dumps(test_request, indent=2)}")
        
        # Use the corrected variable name here as well
        result = await root_agent.process_request(test_request) 
        print("ðŸ“¬ Test Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        logger.debug("Local agent test finished.")
    
    asyncio.run(test_agent())
