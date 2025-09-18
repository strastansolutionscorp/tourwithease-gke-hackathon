# agents/context_specialist.py
from agents.base_agent import ADKAgent, Memory, A2AMessage, Tool
from typing import Dict, Any
import httpx
import asyncio


class WeatherTool(Tool):
    """Tool for getting weather information"""
    def __init__(self):
        super().__init__(
            name="weather",
            description="Get weather information for travel destinations"
        )
        async def execute(self, location: str, date: str = None) -> Dict[str, Any]:
            """Get weather for location"""
            # Simplified weather data - in production, use real weather API
            weather_data = {
            "PAR": "Mild temperatures, occasional rain. Pack layers and an
            umbrella.",
            "LON": "Cool and rainy. Bring warm clothes and waterproof
            jacket.",
            "NYC": "Varies by season. Check current forecast.",
            "LAX": "Warm and sunny most days. Light clothing recommended.",
            "TYO": "Humid in summer, cool in winter. Check seasonal weather."
        }

        return {
            "status": "success",
            "location": location,
            "forecast": weather_data.get(location, "Check local weather forecast before traveling."),
            "source": "weather_service"
        }


class CurrencyTool(Tool):
    """Tool for currency exchange information"""
    def __init__(self):
        super().__init__(
            name="currency",
            description="Get currency exchange rates and money tips"
        )
    async def execute(self, destination: str) -> Dict[str, Any]:
    """Get currency info for destination"""
    # Simplified currency data - in production, use real exchange API
    currency_data = {
        "PAR": {
        "currency": "EUR",
        "symbol": "€",
        "tip": "Credit cards widely accepted. Some places prefer cash.",
        "approximate_rate": "1 USD = 0.92 EUR"
        },
        "LON": {
        "currency": "GBP",
        "symbol": "£",
        "tip": "Contactless payments very common. Pound is strong
        currency.",
        "approximate_rate": "1 USD = 0.79 GBP"
        },
        "TYO": {
        "currency": "JPY",
        "symbol": "¥",
        "tip": "Cash still important in Japan. Get yen from convenience store ATMs.",
        "approximate_rate": "1 USD = 150 JPY"
        }
    }

    return {
        "status": "success",
        "destination": destination,
        "currency_info": currency_data.get(destination, {
        "currency": "Local currency",
        "tip": "Check current exchange rates and payment methods."
        })
    }


class CulturalTipsTool(Tool):
    """Tool for cultural information and tips"""
    def __init__(self):
        super().__init__(
        name="cultural_tips",
        description="Get cultural insights and travel tips"
    )

    async def execute(self, destination: str, trip_type: str = "leisure") -> Dict[str, Any]:
        """Get cultural tips for destination"""

        cultural_data = {
            "PAR": {
                "greeting": "Bonjour/Bonsoir - always greet before asking questions",
                "dining": "Lunch 12-2pm, Dinner after 7:30pm. Tipping 5-10%",
                "customs": "Dress nicely when dining out. Many shops close Sunday/Monday",
                "language": "Learn basic French phrases - locals appreciate the effort"
            },
            "LON": {
                "greeting": "Queue politely and mind the gap on the tube",
                "dining": "Pub culture important. Tipping 10-15% at restaurants",
                "customs": "Weather chat is common. Umbrella essential",
                "language": "English with British spellings and expressions"
            },
            "TYO": {
                "greeting": "Bow slightly. Remove shoes when entering homes/some restaurants",
                "dining": "Don't tip - it's not customary. Slurping ramen is acceptable",
                "customs": "Be quiet on trains. Cash still important",
                "language": "Learn basic Japanese phrases. Many signs in English"
            }
        }


        base_info = cultural_data.get(destination, {
            "greeting": "Research local greeting customs",
            "dining": "Learn about local dining etiquette",
            "customs": "Respect local customs and traditions",
            "language": "Learn basic phrases in local language"
        })
        # Add trip-type specific tips
        if trip_type == "romantic":
            base_info["romantic_tip"] = "Research romantic restaurants and sunset viewpoints"
        elif trip_type == "business":
            base_info["business_tip"] = "Learn business card etiquette and meeting customs"
        elif trip_type == "family":
            base_info["family_tip"] = "Research family-friendly activities and
        child-safe areas"
            
        return {
            "status": "success",
            "destination": destination,
            "cultural_info": base_info
        }


class ContextSpecialist(ADKAgent):
"""Specialized agent for travel context, weather, currency, and cultural information"""
    def __init__(self):
        tools = [
        WeatherTool(),
        CurrencyTool(),
        CulturalTipsTool()
        ]
        super().__init__(
            name="context-specialist",
            description="Provides weather, currency, cultural, and contextual
            travel information",
            tools=tools,
            memory=Memory(memory_type="conversation_buffer", k=10)
        )
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process direct context requests"""
        action = request.get("action", "get_context")
        params = request.get("parameters", {})
        if action == "get_travel_context":
            return await self._get_travel_context(params)
        elif action == "get_weather":
            return await self._get_weather(params)
        elif action == "get_currency":
            return await self._get_currency(params)
        elif action == "get_cultural_tips":
            return await self._get_cultural_tips(params)
        else:

        return {
            "status": "error",
            "message": f"Unknown action: {action}"
        }


    async def process_a2a_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Handle A2A requests from other agents"""
        payload = message.payload
        action = payload.get("action")
        parameters = payload.get("parameters", {})
        self.logger.info(f"Processing A2A request: {action} from {message.from_agent}")
        if action == "get_travel_context":
            return await self._get_travel_context(parameters)
        else:
             return await self.process_request({"action": action, "parameters":
        parameters})

    async def _get_travel_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive travel context"""
        try:
            destination = params.get("destination", "PAR")
            trip_type = params.get("trip_type", "leisure")
            travel_date = params.get("travel_date")

            # Gather context from multiple sources in parallel
            tasks = [
                self.use_tool("weather", location=destination,
                date=travel_date),
                self.use_tool("currency", destination=destination),
                self.use_tool("cultural_tips", destination=destination,
                trip_type=trip_type)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Combine results
            context = {
            "status": "success",
            "destination": destination,
            "trip_type": trip_type
            }

            # Weather information
            if isinstance(results[0], dict) and results[0].get("status") == "success":
                context["weather"] = results[0]["forecast"]
            
            # Currency information
            if isinstance(results[1], dict) and results[1].get("status") == "success":
                context["currency"] = results[1]["currency_info"]
            
            # Cultural tips
            if isinstance(results[2], dict) and results[2].get("status") == "success":
                context["cultural_tips"] = results[2]["cultural_info"]
            
            # Generate summary
            context["summary"] = self._generate_context_summary(context)
            # Store in memory
            self.memory.add_message( "system", f"Provided travel context for {destination} ({trip_type} trip)" )
            return context

        except Exception as e:
            self.logger.error(f"Context gathering error: {e}")
            return {
                "status": "error",
                "message": f"Failed to gather travel context: {str(e)}",
                "parameters": params
            }

def _generate_context_summary(self, context: Dict[str, Any]) -> str:
    """Generate a summary of travel context"""
    summary_parts = []
    if "weather" in context:
    summary_parts.append(f"Weather: {context['weather']}") 🌐 DAY 2 CONTINUED: 
    API GATEWAY & KUBERNETES DEPLOYMENT FastAPI Gateway with WebSocket Support
    API Gateway Implementation

    if "currency" in context and "tip" in context["currency"]:
        summary_parts.append(f"Money: {context['currency']['tip']}")

    if "cultural_tips" in context and "greeting" in context["cultural_tips"]:
        summary_parts.append(f"Culture: {context['cultural_tips'] ['greeting']}")

    if summary_parts:
        return " | ".join(summary_parts)
    else:
        return "General travel information gathered."

    async def _get_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather information"""
        location = params.get("location")
        date = params.get("date")
        return await self.use_tool("weather", location=location, date=date)
        async def _get_currency(self, params: Dict[str, Any]) -> Dict[str, Any]:

        """Get currency information"""
        destination = params.get("destination")
        return await self.use_tool("currency", destination=destination)
        async def _get_cultural_tips(self, params: Dict[str, Any]) -> Dict[str, Any]:
            
        """Get cultural tips"""
        destination = params.get("destination")
        trip_type = params.get("trip_type", "leisure")
        return await self.use_tool("cultural_tips", destination=destination, trip_type=trip_type)
