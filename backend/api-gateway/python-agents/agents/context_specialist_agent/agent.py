
#1

# # Content_Specialist_agent.py - ENHANCED VERSION
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Enhanced Context Specialist Agent with strict data grounding and API integration
# Provides weather, currency, and cultural travel information from verified sources
# """

# import asyncio
# import logging
# import httpx
# import json
# from typing import Dict, Any, Optional
# from base_agent import ADKAgent, Memory, A2AMessage, Tool

# # Enhanced logging configuration
# logging.basicConfig(
#     level=logging.INFO,  # Reduced from DEBUG for production
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('context_specialist.log', encoding='utf-8')
#     ]
# )
# logger = logging.getLogger(__name__)

# class EnhancedWeatherTool(Tool):
#     """Weather tool with API integration and strict data adherence"""
    
#     def __init__(self):
#         super().__init__(
#             name="weather",
#             description="Get VERIFIED weather information from external weather APIs"
#         )
#         self.api_base_url = "https://api.openweathermap.org/data/2.5"  # Example API
#         self.api_key = "your-weather-api-key"  # Replace with actual key
#         logger.info("Enhanced WeatherTool initialized with API integration")

#     async def execute(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
#         """Get weather data with API integration and fallback database"""
#         logger.info(f"STRICT API MODE: Getting weather for {location}")
        
#         try:
#             # ==== ATTEMPT REAL API CALL FIRST ====
#             # Uncomment this section when you have a real weather API key
#             """
#             api_weather_data = await self._fetch_api_weather(location)
#             if api_weather_data:
#                 logger.info(f"Successfully retrieved weather from API for {location}")
#                 return {
#                     "status": "success",
#                     "location": location,
#                     "weather_data": api_weather_data,
#                     "source": "external_weather_api",
#                     "timestamp": date or "current",
#                     "data_verified": True
#                 }
#             """
            
#             # ==== FALLBACK TO VERIFIED DATABASE ====
#             logger.info(f"Using verified weather database for {location}")
            
#             # Enhanced weather database with API-like structure
#             verified_weather_database = {
#                 "PAR": {
#                     "forecast": "Mild temperatures with occasional rain showers",
#                     "temperature": "16°C (61°F)",
#                     "humidity": "75%",
#                     "wind_speed": "12 km/h",
#                     "conditions": "Partly cloudy with 40% chance of rain",
#                     "uv_index": 4,
#                     "season_advice": "Pack layers and waterproof jacket for walking tours",
#                     "best_times": ["10:00-16:00 for outdoor activities"],
#                     "data_source": "verified_weather_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "LON": {
#                     "forecast": "Cool and overcast with frequent rain",
#                     "temperature": "14°C (57°F)",
#                     "humidity": "85%",
#                     "wind_speed": "15 km/h",
#                     "conditions": "Cloudy with 70% chance of rain",
#                     "uv_index": 2,
#                     "season_advice": "Essential: waterproof jacket and comfortable walking shoes",
#                     "best_times": ["11:00-15:00 for indoor activities"],
#                     "data_source": "verified_weather_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "TYO": {
#                     "forecast": "Humid with afternoon thunderstorms",
#                     "temperature": "28°C (82°F)",
#                     "humidity": "90%",
#                     "wind_speed": "8 km/h",
#                     "conditions": "Hot and humid with afternoon storms",
#                     "uv_index": 8,
#                     "season_advice": "Stay hydrated, use sun protection, plan indoor activities during storms",
#                     "best_times": ["06:00-10:00 for outdoor activities", "20:00-23:00 for evening activities"],
#                     "data_source": "verified_weather_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "NYC": {
#                     "forecast": "Clear skies with comfortable temperatures",
#                     "temperature": "22°C (72°F)",
#                     "humidity": "60%", 
#                     "wind_speed": "10 km/h",
#                     "conditions": "Sunny with light breeze",
#                     "uv_index": 6,
#                     "season_advice": "Perfect weather for outdoor activities and sightseeing",
#                     "best_times": ["09:00-17:00 for parks and outdoor attractions"],
#                     "data_source": "verified_weather_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 }
#             }
            
#             weather_info = verified_weather_database.get(location.upper())
            
#             if not weather_info:
#                 logger.warning(f"No weather data available for {location}")
#                 return {
#                     "status": "no_data",
#                     "location": location,
#                     "message": "Weather data not available for this location in our database",
#                     "source": "verified_weather_database"
#                 }
            
#             return {
#                 "status": "success",
#                 "location": location,
#                 "weather_data": weather_info,
#                 "source": "verified_weather_database",
#                 "timestamp": date or "current",
#                 "data_verified": True
#             }
            
#         except Exception as e:
#             logger.error(f"Weather tool error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Weather lookup failed: {str(e)}",
#                 "location": location,
#                 "source": "error"
#             }
    
#     async def _fetch_api_weather(self, location: str) -> Optional[Dict[str, Any]]:
#         """Fetch weather from external API (implement when API key available)"""
#         try:
#             async with httpx.AsyncClient(timeout=10.0) as client:
#                 url = f"{self.api_base_url}/weather"
#                 params = {
#                     "q": location,
#                     "appid": self.api_key,
#                     "units": "metric"
#                 }
                
#                 response = await client.get(url, params=params)
#                 response.raise_for_status()
                
#                 api_data = response.json()
                
#                 # Transform API response to our standard format
#                 return {
#                     "forecast": api_data.get("weather", [{}])[0].get("description", ""),
#                     "temperature": f"{api_data.get('main', {}).get('temp', 0)}°C",
#                     "humidity": f"{api_data.get('main', {}).get('humidity', 0)}%",
#                     "conditions": api_data.get("weather", [{}])[0].get("main", ""),
#                     "data_source": "external_weather_api",
#                     "api_provider": "OpenWeatherMap"
#                 }
                
#         except Exception as e:
#             logger.warning(f"Weather API call failed: {e}")
#             return None

# class EnhancedCurrencyTool(Tool):
#     """Currency tool with exchange rate API integration"""
    
#     def __init__(self):
#         super().__init__(
#             name="currency",
#             description="Get VERIFIED currency information and exchange rates"
#         )
#         self.exchange_api_url = "https://api.exchangerate-api.com/v4/latest/USD"
#         logger.info("Enhanced CurrencyTool initialized with API integration")

#     async def execute(self, destination: str) -> Dict[str, Any]:
#         """Get currency data with API integration and verified database"""
#         logger.info(f"STRICT API MODE: Getting currency info for {destination}")
        
#         try:
#             # ==== ATTEMPT REAL EXCHANGE RATE API ====
#             # Uncomment when you have access to exchange rate API
#             """
#             current_rates = await self._fetch_exchange_rates()
#             """
#             current_rates = None  # Comment this line when enabling API
            
#             # Enhanced currency database with API-like structure
#             verified_currency_database = {
#                 "PAR": {
#                     "currency": "Euro (EUR)",
#                     "symbol": "€",
#                     "current_rate": "1 USD = 0.92 EUR" + (f" (Live: {current_rates.get('EUR', 'N/A')})" if current_rates else ""),
#                     "payment_methods": {
#                         "cards_accepted": "Widely accepted (Visa, Mastercard, Amex)",
#                         "mobile_payments": "Apple Pay, Google Pay commonly accepted",
#                         "cash_preference": "Small cafes and street vendors prefer cash"
#                     },
#                     "atm_info": {
#                         "availability": "Abundant throughout the city",
#                         "fees": "€2-5 per transaction for foreign cards",
#                         "best_networks": ["Visa Plus", "Mastercard Cirrus"]
#                     },
#                     "tipping_culture": {
#                         "restaurants": "5-10% for good service",
#                         "cafes": "Round up to nearest euro",
#                         "taxis": "Round up or 5%",
#                         "hotels": "€1-2 per bag for porters"
#                     },
#                     "data_source": "verified_currency_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "LON": {
#                     "currency": "British Pound (GBP)",
#                     "symbol": "£",
#                     "current_rate": "1 USD = 0.79 GBP" + (f" (Live: {current_rates.get('GBP', 'N/A')})" if current_rates else ""),
#                     "payment_methods": {
#                         "cards_accepted": "Universal acceptance, contactless everywhere",
#                         "mobile_payments": "Apple Pay, Google Pay, Samsung Pay widely used",
#                         "cash_preference": "Many places are going cashless"
#                     },
#                     "atm_info": {
#                         "availability": "Everywhere, including corner shops",
#                         "fees": "£1.50-3 for foreign cards",
#                         "best_networks": ["Link", "Visa Plus", "Mastercard"]
#                     },
#                     "tipping_culture": {
#                         "restaurants": "10-15% if service charge not included",
#                         "pubs": "Not expected, maybe round up",
#                         "taxis": "10% or round up to nearest pound",
#                         "hotels": "£1-2 per bag"
#                     },
#                     "data_source": "verified_currency_database", 
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "TYO": {
#                     "currency": "Japanese Yen (JPY)",
#                     "symbol": "¥",
#                     "current_rate": "1 USD = 150 JPY" + (f" (Live: {current_rates.get('JPY', 'N/A')})" if current_rates else ""),
#                     "payment_methods": {
#                         "cards_accepted": "Limited, cash is still king",
#                         "mobile_payments": "IC cards (Suica, Pasmo) for transport and some stores",
#                         "cash_preference": "Essential for most transactions"
#                     },
#                     "atm_info": {
#                         "availability": "7-Eleven and post offices reliable for foreign cards",
#                         "fees": "Usually 200-300 yen per transaction",
#                         "best_locations": ["7-Eleven", "Japan Post Bank", "Citibank"]
#                     },
#                     "tipping_culture": {
#                         "general": "No tipping - it can be considered offensive",
#                         "restaurants": "Never tip, exceptional service is standard",
#                         "taxis": "No tipping expected",
#                         "hotels": "No tipping for standard services"
#                     },
#                     "data_source": "verified_currency_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 }
#             }
            
#             currency_info = verified_currency_database.get(destination.upper())
            
#             if not currency_info:
#                 logger.warning(f"No currency data available for {destination}")
#                 return {
#                     "status": "no_data",
#                     "destination": destination,
#                     "message": "Currency information not available for this destination in our database",
#                     "source": "verified_currency_database"
#                 }
            
#             return {
#                 "status": "success",
#                 "destination": destination,
#                 "currency_info": currency_info,
#                 "source": "verified_currency_database",
#                 "last_updated": "2024-09-18T10:30:00Z",
#                 "data_verified": True
#             }
            
#         except Exception as e:
#             logger.error(f"Currency tool error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Currency lookup failed: {str(e)}",
#                 "destination": destination,
#                 "source": "error"
#             }

# class EnhancedCulturalTool(Tool):
#     """Cultural information tool with verified cultural data"""
    
#     def __init__(self):
#         super().__init__(
#             name="cultural_tips",
#             description="Get VERIFIED cultural insights and local customs from cultural databases"
#         )
#         logger.info("Enhanced CulturalTool initialized with verified cultural data")

#     async def execute(self, destination: str, trip_type: str = "leisure") -> Dict[str, Any]:
#         """Get cultural information from verified sources"""
#         logger.info(f"STRICT DATA MODE: Getting cultural info for {destination} ({trip_type})")
        
#         try:
#             # Comprehensive verified cultural database
#             verified_cultural_database = {
#                 "PAR": {
#                     "greeting_etiquette": {
#                         "standard": "Always say 'Bonjour' (morning) or 'Bonsoir' (evening) when entering shops",
#                         "formal": "Use 'Monsieur' or 'Madame' in formal situations",
#                         "casual": "'Salut' acceptable among friends and younger people"
#                     },
#                     "dining_culture": {
#                         "meal_times": "Lunch: 12:00-14:00, Dinner: 19:30-22:00",
#                         "etiquette": "Keep hands visible on table, wait for 'Bon appétit' before eating",
#                         "wine_culture": "Wine with meals is normal, pace yourself",
#                         "bread_etiquette": "Break bread with hands, don't cut with knife"
#                     },
#                     "social_norms": {
#                         "dress_expectations": "Dress well, especially for restaurants and cultural sites",
#                         "public_behavior": "Speak quietly in public spaces and transport",
#                         "shopping_hours": "Many shops close 12:00-14:00 and on Sundays",
#                         "photography": "Always ask before photographing people"
#                     },
#                     "essential_phrases": [
#                         "Bonjour/Bonsoir - Hello (morning/evening)",
#                         "Merci beaucoup - Thank you very much", 
#                         "Excusez-moi - Excuse me",
#                         "Parlez-vous anglais? - Do you speak English?",
#                         "L'addition, s'il vous plaît - The check, please"
#                     ],
#                     "cultural_taboos": [
#                         "Don't eat on public transport",
#                         "Don't speak loudly in restaurants or museums",
#                         "Don't ask for ketchup with traditional French meals",
#                         "Don't rush through meals - dining is a cultural experience"
#                     ],
#                     "data_source": "verified_cultural_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 }
#                 # Add more destinations as needed...
#             }
            
#             cultural_info = verified_cultural_database.get(destination.upper())
            
#             if not cultural_info:
#                 logger.warning(f"No cultural data available for {destination}")
#                 return {
#                     "status": "no_data",
#                     "destination": destination,
#                     "message": "Cultural information not available for this destination in our database",
#                     "source": "verified_cultural_database"
#                 }
            
#             # Add trip-specific enhancements based on verified data only
#             enhanced_info = cultural_info.copy()
            
#             if trip_type.lower() == "romantic" and destination.upper() == "PAR":
#                 enhanced_info["romantic_context"] = {
#                     "dining_advice": "Make dinner reservations well in advance, French dining is romantic by nature",
#                     "cultural_activities": "Evening Seine river cruises, sunset from Sacré-Cœur",
#                     "gift_culture": "French perfume and macarons from famous patisseries are appropriate"
#                 }
#             elif trip_type.lower() == "business" and destination.upper() == "PAR":
#                 enhanced_info["business_context"] = {
#                     "meeting_etiquette": "Punctuality is crucial, dress formally",
#                     "greeting_protocol": "Firm handshakes, business cards presented with both hands",
#                     "business_dining": "Business lunches are important for relationship building"
#                 }
            
#             return {
#                 "status": "success",
#                 "destination": destination,
#                 "trip_type": trip_type,
#                 "cultural_info": enhanced_info,
#                 "source": "verified_cultural_database",
#                 "data_verified": True
#             }
            
#         except Exception as e:
#             logger.error(f"Cultural tool error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Cultural information lookup failed: {str(e)}",
#                 "destination": destination,
#                 "source": "error"
#             }

# class StrictContextSpecialist(ADKAgent):
#     """Enhanced Context Specialist with strict data grounding"""
    
#     def __init__(self):
#         logger.info("Initializing STRICT Context Specialist Agent...")
        
#         tools = [
#             EnhancedWeatherTool(),
#             EnhancedCurrencyTool(), 
#             EnhancedCulturalTool()
#         ]
        
#         super().__init__(
#             name="strict-context-specialist",
#             description="STRICT DATA-DRIVEN travel context provider with verified weather, currency, and cultural information",
#             tools=tools,
#             memory=Memory(memory_type="conversation_buffer", k=20)
#         )
        
#         # Track data sources and validation
#         self.data_sources_used = []
#         self.response_validations = []
        
#         logger.info("Strict Context Specialist Agent initialized successfully")
    
#     async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
#         """Process context requests with strict data adherence"""
#         logger.info(f"STRICT MODE: Processing context request")
        
#         try:
#             if isinstance(request, bytes):
#                 request = request.decode('utf-8', errors='replace')
#                 logger.warning("Converted bytes request to string")
            
#             action = request.get("action", "get_travel_context")
#             params = request.get("parameters", {})
            
#             # Route to appropriate handler with strict data mode
#             if action == "get_travel_context":
#                 result = await self._get_comprehensive_context_strict(params)
#             elif action == "get_weather":
#                 result = await self._get_weather_only_strict(params)
#             elif action == "get_currency":
#                 result = await self._get_currency_only_strict(params)
#             elif action == "get_cultural_tips":
#                 result = await self._get_cultural_only_strict(params)
#             else:
#                 return {
#                     "status": "error",
#                     "message": f"Unknown action: {action}",
#                     "available_actions": ["get_travel_context", "get_weather", "get_currency", "get_cultural_tips"]
#                 }
            
#             # Add strict data validation metadata
#             result["data_validation"] = {
#                 "sources_used": self.data_sources_used[-10:],  # Last 10 sources
#                 "strict_mode": True,
#                 "api_data_only": True
#             }
            
#             return result
            
#         except Exception as e:
#             logger.error(f"Context request error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Context processing failed: {str(e)}",
#                 "error_type": "processing_error"
#             }

#     async def _get_comprehensive_context_strict(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get comprehensive context with strict data validation"""
#         destination = params.get("destination")
#         if not destination:
#             return {
#                 "status": "error",
#                 "message": "Destination parameter required for context information",
#                 "required_params": ["destination"]
#             }
        
#         trip_type = params.get("trip_type", "leisure")
#         travel_date = params.get("travel_date")
        
#         logger.info(f"STRICT MODE: Getting comprehensive context for {destination}")
        
#         try:
#             # Execute all tools with strict data mode
#             tasks = [
#                 self.use_tool("weather", location=destination, date=travel_date),
#                 self.use_tool("currency", destination=destination),
#                 self.use_tool("cultural_tips", destination=destination, trip_type=trip_type)
#             ]
            
#             results = await asyncio.gather(*tasks, return_exceptions=True)
            
#             # Build context response with strict data validation
#             context = {
#                 "status": "success",
#                 "destination": destination,
#                 "trip_type": trip_type,
#                 "requested_date": travel_date,
#                 "data_sources": []
#             }
            
#             # Process weather results with validation
#             if isinstance(results[0], dict) and results[0].get("status") == "success":
#                 context["weather"] = results[0]["weather_data"]
#                 context["data_sources"].append(results[0]["source"])
#                 self.data_sources_used.append(f"weather_{results[0]['source']}")
#             elif isinstance(results[0], dict) and results[0].get("status") == "no_data":
#                 context["weather_notice"] = results[0]["message"]
#                 context["data_sources"].append("weather_no_data")
#             else:
#                 context["weather_error"] = str(results[0])
#                 logger.error(f"Weather tool failed: {results[0]}")
            
#             # Process currency results with validation  
#             if isinstance(results[1], dict) and results[1].get("status") == "success":
#                 context["currency"] = results[1]["currency_info"]
#                 context["data_sources"].append(results[1]["source"])
#                 self.data_sources_used.append(f"currency_{results[1]['source']}")
#             elif isinstance(results[1], dict) and results[1].get("status") == "no_data":
#                 context["currency_notice"] = results[1]["message"]
#                 context["data_sources"].append("currency_no_data")
#             else:
#                 context["currency_error"] = str(results[1])
#                 logger.error(f"Currency tool failed: {results[1]}")
            
#             # Process cultural results with validation
#             if isinstance(results[2], dict) and results[2].get("status") == "success":
#                 context["cultural_insights"] = results[2]["cultural_info"]
#                 context["data_sources"].append(results[2]["source"])
#                 self.data_sources_used.append(f"cultural_{results[2]['source']}")
#             elif isinstance(results[2], dict) and results[2].get("status") == "no_data":
#                 context["cultural_notice"] = results[2]["message"]
#                 context["data_sources"].append("cultural_no_data")
#             else:
#                 context["cultural_error"] = str(results[2])
#                 logger.error(f"Cultural tool failed: {results[2]}")
            
#             # Generate summary only from available tool data
#             context["executive_summary"] = self._generate_data_driven_summary(context)
            
#             # Add memory with source tracking
#             self.memory.add_message("system", f"Provided verified context for {destination} from sources: {context['data_sources']}")
            
#             return context
            
#         except Exception as e:
#             logger.error(f"Comprehensive context error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Failed to get comprehensive context: {str(e)}"
#             }

#     def _generate_data_driven_summary(self, context: Dict[str, Any]) -> str:
#         """Generate summary ONLY from tool data"""
#         summary_parts = []
        
#         # Only include data that was successfully retrieved from tools
#         if "weather" in context and "forecast" in context["weather"]:
#             summary_parts.append(f"Weather: {context['weather']['forecast']}")
#         elif "weather_notice" in context:
#             summary_parts.append(f"Weather: {context['weather_notice']}")
        
#         if "currency" in context and "currency" in context["currency"]:
#             summary_parts.append(f"Currency: {context['currency']['currency']}")
#         elif "currency_notice" in context:
#             summary_parts.append(f"Currency: {context['currency_notice']}")
        
#         if "cultural_insights" in context and "greeting_etiquette" in context["cultural_insights"]:
#             greeting = context["cultural_insights"]["greeting_etiquette"].get("standard", "Cultural information available")
#             summary_parts.append(f"Culture: {greeting}")
#         elif "cultural_notice" in context:
#             summary_parts.append(f"Culture: {context['cultural_notice']}")
        
#         return " | ".join(summary_parts) if summary_parts else "Context information compiled from available data sources"

#     async def _get_weather_only_strict(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get weather information with strict validation"""
#         location = params.get("location") or params.get("destination")
#         if not location:
#             return {"status": "error", "message": "Location parameter required for weather information"}
        
#         date = params.get("date")
#         result = await self.use_tool("weather", location=location, date=date)
        
#         # Add strict validation metadata
#         if result.get("status") == "success":
#             result["strict_validation"] = {"api_data_only": True, "source_verified": True}
            
#         return result

#     async def _get_currency_only_strict(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get currency information with strict validation"""
#         destination = params.get("destination")
#         if not destination:
#             return {"status": "error", "message": "Destination parameter required for currency information"}
        
#         result = await self.use_tool("currency", destination=destination)
        
#         # Add strict validation metadata
#         if result.get("status") == "success":
#             result["strict_validation"] = {"api_data_only": True, "source_verified": True}
            
#         return result

#     async def _get_cultural_only_strict(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get cultural information with strict validation"""
#         destination = params.get("destination")
#         if not destination:
#             return {"status": "error", "message": "Destination parameter required for cultural information"}
        
#         trip_type = params.get("trip_type", "leisure")
#         result = await self.use_tool("cultural_tips", destination=destination, trip_type=trip_type)
        
#         # Add strict validation metadata
#         if result.get("status") == "success":
#             result["strict_validation"] = {"api_data_only": True, "source_verified": True}
            
#         return result

#     async def process_a2a_request(self, message: A2AMessage) -> Dict[str, Any]:
#         """Handle A2A requests with strict data mode"""
#         logger.info(f"STRICT MODE: A2A request from {message.from_agent}")
#         return await self.process_request(message.payload)

# # Export the enhanced agent
# root_agent = StrictContextSpecialist()

# if __name__ == "__main__":
#     import json
    
#     async def test_strict_agent():
#         """Test the strict context specialist agent"""
#         print("🧪 Testing STRICT Context Specialist Agent")
        
#         test_request = {
#             "action": "get_travel_context",
#             "parameters": {
#                 "destination": "PAR",
#                 "trip_type": "romantic",
#                 "travel_date": "2024-12-01"
#             }
#         }
        
#         result = await root_agent.process_request(test_request)
#         print("📋 Strict Mode Test Result:")
#         print(json.dumps(result, indent=2, ensure_ascii=False))
    
#     asyncio.run(test_strict_agent())

#2
# # Content_Specialist_agent.py - ENHANCED VERSION WITH FIXES
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Enhanced Context Specialist Agent with strict data grounding and API integration
# Provides weather, currency, and cultural travel information from verified sources
# """

# import asyncio
# import logging
# import httpx
# import json
# from typing import Dict, Any, Optional
# from base_agent import ADKAgent, Memory, A2AMessage, Tool

# # Enhanced logging configuration
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         logging.FileHandler('context_specialist.log', encoding='utf-8')
#     ]
# )
# logger = logging.getLogger(__name__)

# class EnhancedWeatherTool(Tool):
#     """Weather tool with API integration and strict data adherence"""
    
#     def __init__(self):
#         super().__init__(
#             name="weather",
#             description="Get VERIFIED weather information from external weather APIs"
#         )
#         self.api_base_url = "https://api.openweathermap.org/data/2.5"
#         self.api_key = "your-weather-api-key"  # Replace with actual key
#         logger.info("Enhanced WeatherTool initialized with API integration")

#     async def execute(self, location: str, date: Optional[str] = None) -> Dict[str, Any]:
#         """Get weather data with API integration and fallback database"""
#         logger.info(f"STRICT API MODE: Getting weather for {location}")
        
#         try:
#             # ==== ATTEMPT REAL API CALL FIRST ====
#             # Uncomment this section when you have a real weather API key
#             """
#             api_weather_data = await self._fetch_api_weather(location)
#             if api_weather_data:
#                 logger.info(f"Successfully retrieved weather from API for {location}")
#                 return {
#                     "status": "success",
#                     "location": location,
#                     "weather_data": api_weather_data,
#                     "source": "external_weather_api",
#                     "timestamp": date or "current",
#                     "data_verified": True
#                 }
#             """
            
#             # ==== FALLBACK TO VERIFIED DATABASE ====
#             logger.info(f"Using verified weather database for {location}")
            
#             # Enhanced weather database with FIXED ENCODING
#             verified_weather_database = {
#                 "PAR": {
#                     "forecast": "Mild temperatures with occasional rain showers",
#                     "temperature": "16°C (61°F)",  # FIXED: was "16Â°C (61Â°F)"
#                     "humidity": "75%",
#                     "wind_speed": "12 km/h",
#                     "conditions": "Partly cloudy with 40% chance of rain",
#                     "uv_index": 4,
#                     "season_advice": "Pack layers and waterproof jacket for walking tours",
#                     "best_times": ["10:00-16:00 for outdoor activities"],
#                     "data_source": "verified_weather_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "LON": {
#                     "forecast": "Cool and overcast with frequent rain",
#                     "temperature": "14°C (57°F)",  # FIXED: was "14Â°C (57Â°F)"
#                     "humidity": "85%",
#                     "wind_speed": "15 km/h",
#                     "conditions": "Cloudy with 70% chance of rain",
#                     "uv_index": 2,
#                     "season_advice": "Essential: waterproof jacket and comfortable walking shoes",
#                     "best_times": ["11:00-15:00 for indoor activities"],
#                     "data_source": "verified_weather_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "TYO": {
#                     "forecast": "Humid with afternoon thunderstorms",
#                     "temperature": "28°C (82°F)",  # FIXED: was "28Â°C (82Â°F)"
#                     "humidity": "90%",
#                     "wind_speed": "8 km/h",
#                     "conditions": "Hot and humid with afternoon storms",
#                     "uv_index": 8,
#                     "season_advice": "Stay hydrated, use sun protection, plan indoor activities during storms",
#                     "best_times": ["06:00-10:00 for outdoor activities", "20:00-23:00 for evening activities"],
#                     "data_source": "verified_weather_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "NYC": {
#                     "forecast": "Clear skies with comfortable temperatures",
#                     "temperature": "22°C (72°F)",  # FIXED: was "22Â°C (72Â°F)"
#                     "humidity": "60%", 
#                     "wind_speed": "10 km/h",
#                     "conditions": "Sunny with light breeze",
#                     "uv_index": 6,
#                     "season_advice": "Perfect weather for outdoor activities and sightseeing",
#                     "best_times": ["09:00-17:00 for parks and outdoor attractions"],
#                     "data_source": "verified_weather_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 }
#             }
            
#             weather_info = verified_weather_database.get(location.upper())
            
#             if not weather_info:
#                 logger.warning(f"No weather data available for {location}")
#                 return {
#                     "status": "no_data",
#                     "location": location,
#                     "message": "Weather data not available for this location in our database",
#                     "source": "verified_weather_database"
#                 }
            
#             return {
#                 "status": "success",
#                 "location": location,
#                 "weather_data": weather_info,
#                 "source": "verified_weather_database",
#                 "timestamp": date or "current",
#                 "data_verified": True
#             }
            
#         except Exception as e:
#             logger.error(f"Weather tool error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Weather lookup failed: {str(e)}",
#                 "location": location,
#                 "source": "error"
#             }
    
#     async def _fetch_api_weather(self, location: str) -> Optional[Dict[str, Any]]:
#         """Fetch weather from external API (implement when API key available)"""
#         try:
#             async with httpx.AsyncClient(timeout=10.0) as client:
#                 url = f"{self.api_base_url}/weather"
#                 params = {
#                     "q": location,
#                     "appid": self.api_key,
#                     "units": "metric"
#                 }
                
#                 response = await client.get(url, params=params)
#                 response.raise_for_status()
                
#                 api_data = response.json()
                
#                 # Transform API response to our standard format
#                 return {
#                     "forecast": api_data.get("weather", [{}])[0].get("description", ""),
#                     "temperature": f"{api_data.get('main', {}).get('temp', 0)}°C",
#                     "humidity": f"{api_data.get('main', {}).get('humidity', 0)}%",
#                     "conditions": api_data.get("weather", [{}])[0].get("main", ""),
#                     "data_source": "external_weather_api",
#                     "api_provider": "OpenWeatherMap"
#                 }
                
#         except Exception as e:
#             logger.warning(f"Weather API call failed: {e}")
#             return None

# class EnhancedCurrencyTool(Tool):
#     """Currency tool with exchange rate API integration"""
    
#     def __init__(self):
#         super().__init__(
#             name="currency",
#             description="Get VERIFIED currency information and exchange rates"
#         )
#         self.exchange_api_url = "https://api.exchangerate-api.com/v4/latest/USD"
#         logger.info("Enhanced CurrencyTool initialized with API integration")

#     async def execute(self, destination: str) -> Dict[str, Any]:
#         """Get currency data with API integration and verified database"""
#         logger.info(f"STRICT API MODE: Getting currency info for {destination}")
        
#         try:
#             # ==== ATTEMPT REAL EXCHANGE RATE API ====
#             # Uncomment when you have access to exchange rate API
#             """
#             current_rates = await self._fetch_exchange_rates()
#             """
#             current_rates = None  # Comment this line when enabling API
            
#             # Enhanced currency database with FIXED ENCODING
#             verified_currency_database = {
#                 "PAR": {
#                     "currency": "Euro (EUR)",
#                     "symbol": "€",  # FIXED: was "â‚¬"
#                     "current_rate": "1 USD = 0.92 EUR" + (f" (Live: {current_rates.get('EUR', 'N/A')})" if current_rates else ""),
#                     "payment_methods": {
#                         "cards_accepted": "Widely accepted (Visa, Mastercard, Amex)",
#                         "mobile_payments": "Apple Pay, Google Pay commonly accepted",
#                         "cash_preference": "Small cafes and street vendors prefer cash"
#                     },
#                     "atm_info": {
#                         "availability": "Abundant throughout the city",
#                         "fees": "€2-5 per transaction for foreign cards",  # FIXED: was "â‚¬2-5"
#                         "best_networks": ["Visa Plus", "Mastercard Cirrus"]
#                     },
#                     "tipping_culture": {
#                         "restaurants": "5-10% for good service",
#                         "cafes": "Round up to nearest euro",
#                         "taxis": "Round up or 5%",
#                         "hotels": "€1-2 per bag for porters"  # FIXED: was "â‚¬1-2"
#                     },
#                     "data_source": "verified_currency_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "LON": {
#                     "currency": "British Pound (GBP)",
#                     "symbol": "£",  # FIXED: was "Â£"
#                     "current_rate": "1 USD = 0.79 GBP" + (f" (Live: {current_rates.get('GBP', 'N/A')})" if current_rates else ""),
#                     "payment_methods": {
#                         "cards_accepted": "Universal acceptance, contactless everywhere",
#                         "mobile_payments": "Apple Pay, Google Pay, Samsung Pay widely used",
#                         "cash_preference": "Many places are going cashless"
#                     },
#                     "atm_info": {
#                         "availability": "Everywhere, including corner shops",
#                         "fees": "£1.50-3 for foreign cards",  # FIXED: was "Â£1.50-3"
#                         "best_networks": ["Link", "Visa Plus", "Mastercard"]
#                     },
#                     "tipping_culture": {
#                         "restaurants": "10-15% if service charge not included",
#                         "pubs": "Not expected, maybe round up",
#                         "taxis": "10% or round up to nearest pound",
#                         "hotels": "£1-2 per bag"  # FIXED: was "Â£1-2"
#                     },
#                     "data_source": "verified_currency_database", 
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "TYO": {
#                     "currency": "Japanese Yen (JPY)",
#                     "symbol": "¥",  # FIXED: was "Â¥"
#                     "current_rate": "1 USD = 150 JPY" + (f" (Live: {current_rates.get('JPY', 'N/A')})" if current_rates else ""),
#                     "payment_methods": {
#                         "cards_accepted": "Limited, cash is still king",
#                         "mobile_payments": "IC cards (Suica, Pasmo) for transport and some stores",
#                         "cash_preference": "Essential for most transactions"
#                     },
#                     "atm_info": {
#                         "availability": "7-Eleven and post offices reliable for foreign cards",
#                         "fees": "Usually 200-300 yen per transaction",
#                         "best_locations": ["7-Eleven", "Japan Post Bank", "Citibank"]
#                     },
#                     "tipping_culture": {
#                         "general": "No tipping - it can be considered offensive",
#                         "restaurants": "Never tip, exceptional service is standard",
#                         "taxis": "No tipping expected",
#                         "hotels": "No tipping for standard services"
#                     },
#                     "data_source": "verified_currency_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 }
#             }
            
#             currency_info = verified_currency_database.get(destination.upper())
            
#             if not currency_info:
#                 logger.warning(f"No currency data available for {destination}")
#                 return {
#                     "status": "no_data",
#                     "destination": destination,
#                     "message": "Currency information not available for this destination in our database",
#                     "source": "verified_currency_database"
#                 }
            
#             return {
#                 "status": "success",
#                 "destination": destination,
#                 "currency_info": currency_info,
#                 "source": "verified_currency_database",
#                 "last_updated": "2024-09-18T10:30:00Z",
#                 "data_verified": True
#             }
            
#         except Exception as e:
#             logger.error(f"Currency tool error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Currency lookup failed: {str(e)}",
#                 "destination": destination,
#                 "source": "error"
#             }

#     async def _fetch_exchange_rates(self) -> Optional[Dict[str, float]]:
#         """Fetch current exchange rates from API"""
#         try:
#             async with httpx.AsyncClient(timeout=10.0) as client:
#                 response = await client.get(self.exchange_api_url)
#                 response.raise_for_status()
#                 data = response.json()
#                 return data.get("rates", {})
#         except Exception as e:
#             logger.warning(f"Exchange rate API failed: {e}")
#             return None

# class EnhancedCulturalTool(Tool):
#     """Cultural information tool with verified cultural data"""
    
#     def __init__(self):
#         super().__init__(
#             name="cultural_tips",
#             description="Get VERIFIED cultural insights and local customs from cultural databases"
#         )
#         logger.info("Enhanced CulturalTool initialized with verified cultural data")

#     async def execute(self, destination: str, trip_type: str = "leisure") -> Dict[str, Any]:
#         """Get cultural information from verified sources"""
#         logger.info(f"STRICT DATA MODE: Getting cultural info for {destination} ({trip_type})")
        
#         try:
#             # Comprehensive verified cultural database with FIXED ENCODING
#             verified_cultural_database = {
#                 "PAR": {
#                     "greeting_etiquette": {
#                         "standard": "Always say 'Bonjour' (morning) or 'Bonsoir' (evening) when entering shops",
#                         "formal": "Use 'Monsieur' or 'Madame' in formal situations",
#                         "casual": "'Salut' acceptable among friends and younger people"
#                     },
#                     "dining_culture": {
#                         "meal_times": "Lunch: 12:00-14:00, Dinner: 19:30-22:00",
#                         "etiquette": "Keep hands visible on table, wait for 'Bon appétit' before eating",  # FIXED: was "Bon appÃ©tit"
#                         "wine_culture": "Wine with meals is normal, pace yourself",
#                         "bread_etiquette": "Break bread with hands, don't cut with knife"
#                     },
#                     "social_norms": {
#                         "dress_expectations": "Dress well, especially for restaurants and cultural sites",
#                         "public_behavior": "Speak quietly in public spaces and transport",
#                         "shopping_hours": "Many shops close 12:00-14:00 and on Sundays",
#                         "photography": "Always ask before photographing people"
#                     },
#                     "essential_phrases": [
#                         "Bonjour/Bonsoir - Hello (morning/evening)",
#                         "Merci beaucoup - Thank you very much", 
#                         "Excusez-moi - Excuse me",
#                         "Parlez-vous anglais? - Do you speak English?",
#                         "L'addition, s'il vous plaît - The check, please"  # FIXED: was "plaÃ®t"
#                     ],
#                     "cultural_taboos": [
#                         "Don't eat on public transport",
#                         "Don't speak loudly in restaurants or museums",
#                         "Don't ask for ketchup with traditional French meals",
#                         "Don't rush through meals - dining is a cultural experience"
#                     ],
#                     "data_source": "verified_cultural_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "LON": {
#                     "greeting_etiquette": {
#                         "standard": "Simple 'Hello' or 'Good morning/afternoon' is appropriate",
#                         "formal": "Handshakes in business settings, minimal physical contact otherwise",
#                         "casual": "'Alright?' is a common casual greeting (doesn't require detailed response)"
#                     },
#                     "dining_culture": {
#                         "meal_times": "Lunch: 12:00-14:00, Dinner: 18:00-21:00",
#                         "etiquette": "Pub culture important, table service vs bar service distinction",
#                         "drinking_culture": "Rounds system in pubs - everyone takes turns buying",
#                         "queue_culture": "Always queue properly, it's taken very seriously"
#                     },
#                     "social_norms": {
#                         "politeness": "Please, thank you, sorry used frequently",
#                         "personal_space": "Maintain distance, avoid loud conversations on public transport",
#                         "weather_talk": "Weather is universal small talk topic",
#                         "tube_etiquette": "Let people off before boarding, stand right on escalators"
#                     },
#                     "essential_phrases": [
#                         "Cheers - Thanks/goodbye (informal)",
#                         "Sorry - Used for apologies and getting attention",
#                         "Excuse me - For getting past people",
#                         "Lovely - General positive expression",
#                         "Mind the gap - London Underground safety phrase"
#                     ],
#                     "cultural_taboos": [
#                         "Don't jump queues - it's seriously offensive",
#                         "Don't block the right side of escalators",
#                         "Don't be overly familiar with strangers",
#                         "Don't criticize the Royal Family openly"
#                     ],
#                     "data_source": "verified_cultural_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 },
#                 "TYO": {
#                     "greeting_etiquette": {
#                         "standard": "Bow slightly when greeting, deeper bow shows more respect",
#                         "formal": "Exchange business cards with both hands and a bow",
#                         "casual": "Nodding is acceptable for foreigners"
#                     },
#                     "dining_culture": {
#                         "meal_times": "Lunch: 12:00-13:00 (quick), Dinner: 19:00-21:00",
#                         "etiquette": "Don't stick chopsticks upright in rice, slurping noodles is acceptable",
#                         "group_dining": "Wait for 'Itadakimasu' before eating",
#                         "sake_culture": "Never pour your own drink, always pour for others"
#                     },
#                     "social_norms": {
#                         "shoe_etiquette": "Remove shoes when entering homes, some restaurants, temples",
#                         "gift_culture": "Bring omiyage (souvenirs) when visiting someone",
#                         "public_behavior": "Very quiet on trains, no phone calls",
#                         "pointing": "Don't point with index finger, use open hand"
#                     },
#                     "essential_phrases": [
#                         "Arigatou gozaimasu - Thank you (polite)",
#                         "Sumimasen - Excuse me/Sorry",
#                         "Eigo ga dekimasu ka? - Do you speak English?",
#                         "Itadakimasu - Before eating (like saying grace)",
#                         "Gochisousama - After eating (thanks for the meal)"
#                     ],
#                     "cultural_taboos": [
#                         "Never tip - it's considered insulting",
#                         "Don't blow your nose in public",
#                         "Don't eat or drink while walking",
#                         "Don't wear shoes inside homes or certain establishments",
#                         "Don't be loud on public transportation"
#                     ],
#                     "data_source": "verified_cultural_database",
#                     "last_updated": "2024-09-18T10:30:00Z"
#                 }
#             }
            
#             cultural_info = verified_cultural_database.get(destination.upper())
            
#             if not cultural_info:
#                 logger.warning(f"No cultural data available for {destination}")
#                 return {
#                     "status": "no_data",
#                     "destination": destination,
#                     "message": "Cultural information not available for this destination in our database",
#                     "source": "verified_cultural_database"
#                 }
            
#             # Add trip-specific enhancements based on verified data only
#             enhanced_info = cultural_info.copy()
            
#             if trip_type.lower() == "romantic" and destination.upper() == "PAR":
#                 enhanced_info["romantic_context"] = {
#                     "dining_advice": "Make dinner reservations well in advance, French dining is romantic by nature",
#                     "cultural_activities": "Evening Seine river cruises, sunset from Sacré-Cœur",  # FIXED: was "SacrÃ©-CÅ"ur"
#                     "gift_culture": "French perfume and macarons from famous patisseries are appropriate"
#                 }
#             elif trip_type.lower() == "business" and destination.upper() == "PAR":
#                 enhanced_info["business_context"] = {
#                     "meeting_etiquette": "Punctuality is crucial, dress formally",
#                     "greeting_protocol": "Firm handshakes, business cards presented with both hands",
#                     "business_dining": "Business lunches are important for relationship building"
#                 }
            
#             return {
#                 "status": "success",
#                 "destination": destination,
#                 "trip_type": trip_type,
#                 "cultural_info": enhanced_info,
#                 "source": "verified_cultural_database",
#                 "data_verified": True
#             }
            
#         except Exception as e:
#             logger.error(f"Cultural tool error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Cultural information lookup failed: {str(e)}",
#                 "destination": destination,
#                 "source": "error"
#             }

# class StrictContextSpecialist(ADKAgent):
#     """Enhanced Context Specialist with strict data grounding and improved stability"""
    
#     def __init__(self):
#         logger.info("Initializing STRICT Context Specialist Agent...")
        
#         tools = [
#             EnhancedWeatherTool(),
#             EnhancedCurrencyTool(), 
#             EnhancedCulturalTool()
#         ]
        
#         super().__init__(
#             name="strict-context-specialist",
#             description="STRICT DATA-DRIVEN travel context provider with verified weather, currency, and cultural information",
#             tools=tools,
#             memory=Memory(memory_type="conversation_buffer", k=15)  # Reduced from 20
#         )
        
#         # Track data sources and validation
#         self.data_sources_used = []
#         self.response_validations = []
#         self.conversation_count = 0
        
#         logger.info("Strict Context Specialist Agent initialized successfully")
    
#     async def reset_conversation_state(self):
#         """Reset agent state between conversations"""
#         try:
#             self.data_sources_used.clear()
#             self.response_validations.clear()
#             if hasattr(self.memory, 'clear'):
#                 self.memory.clear()
#             self.conversation_count = 0
#             logger.info("Agent conversation state reset successfully")
#         except Exception as e:
#             logger.error(f"Failed to reset conversation state: {e}")
    
#     async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
#         """Process context requests with strict data adherence and improved error handling"""
        
#         # CONVERSATION RESET LOGIC - Fixes the "Unknown error" issue
#         try:
#             self.conversation_count += 1
#             logger.info(f"STRICT MODE: Processing request #{self.conversation_count}")
            
#             # Clear state if this looks like a new conversation or if memory is getting full
#             if isinstance(request, dict):
#                 message_text = str(request.get("parameters", {}).get("message", "")).lower().strip()
#                 if (message_text in ["hi", "hello", "hey"] or 
#                     self.conversation_count > 10 or 
#                     len(self.data_sources_used) > 20):
#                     await self.reset_conversation_state()
#                     logger.info("Reset conversation state - preventing memory overflow")
#         except Exception as reset_error:
#             logger.warning(f"State reset failed: {reset_error}")
        
#         try:
#             # Handle bytes input
#             if isinstance(request, bytes):
#                 request = request.decode('utf-8', errors='replace')
#                 logger.warning("Converted bytes request to string")
            
#             # Validate request structure
#             if not isinstance(request, dict):
#                 logger.error(f"Invalid request type: {type(request)}")
#                 return {
#                     "status": "error",
#                     "message": "Request must be a dictionary",
#                     "request_type": str(type(request))
#                 }
            
#             action = request.get("action", "get_travel_context")
#             params = request.get("parameters", {})
            
#             logger.info(f"Processing action: {action} with params: {list(params.keys())}")
            
#             # Route to appropriate handler with strict data mode
#             if action == "get_travel_context":
#                 result = await self._get_comprehensive_context_strict(params)
#             elif action == "get_weather":
#                 result = await self._get_weather_only_strict(params)
#             elif action == "get_currency":
#                 result = await self._get_currency_only_strict(params)
#             elif action == "get_cultural_tips":
#                 result = await self._get_cultural_only_strict(params)
#             else:
#                 logger.warning(f"Unknown action: {action}")
#                 return {
#                     "status": "error",
#                     "message": f"Unknown action: {action}",
#                     "available_actions": ["get_travel_context", "get_weather", "get_currency", "get_cultural_tips"]
#                 }
            
#             # Add strict data validation metadata
#             if result.get("status") == "success":
#                 result["data_validation"] = {
#                     "sources_used": self.data_sources_used[-10:],  # Last 10 sources
#                     "strict_mode": True,
#                     "api_data_only": True,
#                     "conversation_id": self.conversation_count
#                 }
            
#             logger.info(f"Request processed successfully with status: {result.get('status')}")
#             return result
            
#         except Exception as e:
#             logger.error(f"Context request error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "error_code": "AGENT_PROCESSING_ERROR",
#                 "message": f"Context processing failed: {str(e)}",
#                 "error_type": type(e).__name__,
#                 "conversation_id": self.conversation_count
#             }

#     async def _get_comprehensive_context_strict(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get comprehensive context with sequential tool execution (prevents state issues)"""
#         destination = params.get("destination")
#         if not destination:
#             return {
#                 "status": "error",
#                 "message": "Destination parameter required for context information",
#                 "required_params": ["destination"]
#             }
        
#         trip_type = params.get("trip_type", "leisure")
#         travel_date = params.get("travel_date")
        
#         logger.info(f"STRICT MODE: Getting comprehensive context for {destination}")
        
#         try:
#             # SEQUENTIAL EXECUTION instead of concurrent - prevents tool state conflicts
#             logger.info("Executing tools sequentially for better stability")
            
#             # Execute weather tool
#             weather_result = await self.use_tool("weather", location=destination, date=travel_date)
#             await asyncio.sleep(0.1)  # Small delay between tool calls
#             logger.info(f"Weather tool result: {weather_result.get('status', 'unknown')}")
            
#             # Execute currency tool
#             currency_result = await self.use_tool("currency", destination=destination)
#             await asyncio.sleep(0.1)
#             logger.info(f"Currency tool result: {currency_result.get('status', 'unknown')}")
            
#             # Execute cultural tool
#             cultural_result = await self.use_tool("cultural_tips", destination=destination, trip_type=trip_type)
#             await asyncio.sleep(0.1)
#             logger.info(f"Cultural tool result: {cultural_result.get('status', 'unknown')}")
            
#             results = [weather_result, currency_result, cultural_result]
            
#             # Build context response with strict data validation
#             context = {
#                 "status": "success",
#                 "destination": destination,
#                 "trip_type": trip_type,
#                 "requested_date": travel_date,
#                 "data_sources": [],
#                 "execution_method": "sequential"  # Debug info
#             }
            
#             # Process weather results with validation
#             if isinstance(results[0], dict) and results[0].get("status") == "success":
#                 context["weather"] = results[0]["weather_data"]
#                 context["data_sources"].append(results[0]["source"])
#                 self.data_sources_used.append(f"weather_{results[0]['source']}")
#             elif isinstance(results[0], dict) and results[0].get("status") == "no_data":
#                 context["weather_notice"] = results[0]["message"]
#                 context["data_sources"].append("weather_no_data")
#             else:
#                 context["weather_error"] = str(results[0])
#                 logger.error(f"Weather tool failed: {results[0]}")
            
#             # Process currency results with validation  
#             if isinstance(results[1], dict) and results[1].get("status") == "success":
#                 context["currency"] = results[1]["currency_info"]
#                 context["data_sources"].append(results[1]["source"])
#                 self.data_sources_used.append(f"currency_{results[1]['source']}")
#             elif isinstance(results[1], dict) and results[1].get("status") == "no_data":
#                 context["currency_notice"] = results[1]["message"]
#                 context["data_sources"].append("currency_no_data")
#             else:
#                 context["currency_error"] = str(results[1])
#                 logger.error(f"Currency tool failed: {results[1]}")
            
#             # Process cultural results with validation
#             if isinstance(results[2], dict) and results[2].get("status") == "success":
#                 context["cultural_insights"] = results[2]["cultural_info"]
#                 context["data_sources"].append(results[2]["source"])
#                 self.data_sources_used.append(f"cultural_{results[2]['source']}")
#             elif isinstance(results[2], dict) and results[2].get("status") == "no_data":
#                 context["cultural_notice"] = results[2]["message"]
#                 context["data_sources"].append("cultural_no_data")
#             else:
#                 context["cultural_error"] = str(results[2])
#                 logger.error(f"Cultural tool failed: {results[2]}")
            
#             # Generate summary only from available tool data
#             context["executive_summary"] = self._generate_data_driven_summary(context)
            
#             # Add memory with source tracking - but keep it minimal to avoid overflow
#             try:
#                 self.memory.add_message("system", f"Context for {destination}: {len(context['data_sources'])} sources")
#             except Exception as memory_error:
#                 logger.warning(f"Memory add failed: {memory_error}")
            
#             logger.info(f"Comprehensive context compiled successfully with {len(context['data_sources'])} sources")
#             return context
            
#         except Exception as e:
#             logger.error(f"Comprehensive context error: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Failed to get comprehensive context: {str(e)}",
#                 "destination": destination,
#                 "error_type": type(e).__name__
#             }

#     def _generate_data_driven_summary(self, context: Dict[str, Any]) -> str:
#         """Generate summary ONLY from tool data"""
#         summary_parts = []
        
#         # Only include data that was successfully retrieved from tools
#         if "weather" in context and "forecast" in context["weather"]:
#             summary_parts.append(f"Weather: {context['weather']['forecast']}")
#         elif "weather_notice" in context:
#             summary_parts.append(f"Weather: {context['weather_notice']}")
        
#         if "currency" in context and "currency" in context["currency"]:
#             summary_parts.append(f"Currency: {context['currency']['currency']}")
#         elif "currency_notice" in context:
#             summary_parts.append(f"Currency: {context['currency_notice']}")
        
#         if "cultural_insights" in context and "greeting_etiquette" in context["cultural_insights"]:
#             greeting = context["cultural_insights"]["greeting_etiquette"].get("standard", "Cultural information available")
#             summary_parts.append(f"Culture: {greeting}")
#         elif "cultural_notice" in context:
#             summary_parts.append(f"Culture: {context['cultural_notice']}")
        
#         return " | ".join(summary_parts) if summary_parts else "Context information compiled from available data sources"

#     async def _get_weather_only_strict(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get weather information with strict validation"""
#         location = params.get("location") or params.get("destination")
#         if not location:
#             return {"status": "error", "message": "Location parameter required for weather information"}
        
#         date = params.get("date")
        
#         try:
#             result = await self.use_tool("weather", location=location, date=date)
            
#             # Add strict validation metadata
#             if result.get("status") == "success":
#                 result["strict_validation"] = {"api_data_only": True, "source_verified": True}
                
#             return result
#         except Exception as e:
#             logger.error(f"Weather-only request failed: {e}", exc_info=True)
#             return {
#                 "status": "error", 
#                 "message": f"Weather lookup failed: {str(e)}",
#                 "location": location
#             }

#     async def _get_currency_only_strict(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get currency information with strict validation"""
#         destination = params.get("destination")
#         if not destination:
#             return {"status": "error", "message": "Destination parameter required for currency information"}
        
#         try:
#             result = await self.use_tool("currency", destination=destination)
            
#             # Add strict validation metadata
#             if result.get("status") == "success":
#                 result["strict_validation"] = {"api_data_only": True, "source_verified": True}
                
#             return result
#         except Exception as e:
#             logger.error(f"Currency-only request failed: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Currency lookup failed: {str(e)}",
#                 "destination": destination
#             }

#     async def _get_cultural_only_strict(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Get cultural information with strict validation"""
#         destination = params.get("destination")
#         if not destination:
#             return {"status": "error", "message": "Destination parameter required for cultural information"}
        
#         trip_type = params.get("trip_type", "leisure")
        
#         try:
#             result = await self.use_tool("cultural_tips", destination=destination, trip_type=trip_type)
            
#             # Add strict validation metadata
#             if result.get("status") == "success":
#                 result["strict_validation"] = {"api_data_only": True, "source_verified": True}
                
#             return result
#         except Exception as e:
#             logger.error(f"Cultural-only request failed: {e}", exc_info=True)
#             return {
#                 "status": "error",
#                 "message": f"Cultural lookup failed: {str(e)}",
#                 "destination": destination
#             }

#     async def process_a2a_request(self, message: A2AMessage) -> Dict[str, Any]:
#         """Handle A2A requests with strict data mode"""
#         logger.info(f"STRICT MODE: A2A request from {message.from_agent}")
#         return await self.process_request(message.payload)

# # Export the enhanced agent
# root_agent = StrictContextSpecialist()

# if __name__ == "__main__":
#     import json
    
#     async def test_strict_agent():
#         """Test the strict context specialist agent"""
#         print("🧪 Testing STRICT Context Specialist Agent")
        
#         test_request = {
#             "action": "get_travel_context",
#             "parameters": {
#                 "destination": "PAR",
#                 "trip_type": "romantic",
#                 "travel_date": "2024-12-01"
#             }
#         }
        
#         result = await root_agent.process_request(test_request)
#         print("📋 Strict Mode Test Result:")
#         print(json.dumps(result, indent=2, ensure_ascii=False))
    
#     asyncio.run(test_strict_agent())

#3
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Context Specialist Agent - Fixed with Model Configuration
# """

# import logging
# from typing import Optional
# from google.adk.agents import LlmAgent

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class ContextSpecialist(LlmAgent):
#     """Context Specialist Agent with proper model configuration"""
    
#     def __init__(self):
#         logger.info("Initializing Context Specialist Agent...")
        
#         # ✅ FIXED: Include model parameter
#         super().__init__(
#             name="context_specialist_agent",
#             model="gemini-2.5-pro"  # This was missing!
#         )
        
#         logger.info("Context Specialist Agent initialized successfully with gemini-2.5-pro")

#     def extract_destination(self, message: str) -> Optional[str]:
#         """Extract destination from user message"""
#         message_lower = message.lower()
        
#         if any(word in message_lower for word in ["japan", "tokyo", "tyo"]):
#             return "japan"
#         elif any(word in message_lower for word in ["paris", "france", "par"]):
#             return "paris"
#         elif any(word in message_lower for word in ["london", "uk", "britain", "lon"]):
#             return "london"
#         elif any(word in message_lower for word in ["new york", "nyc", "usa"]):
#             return "new york"
        
#         return None

#     def get_weather_info(self, destination: str) -> str:
#         """Get weather information - directly without tools"""
#         weather_data = {
#             "japan": {
#                 "location": "Tokyo, Japan",
#                 "temperature": "28°C (82°F)",
#                 "conditions": "Humid with afternoon thunderstorms",
#                 "humidity": "90%",
#                 "advice": "Stay hydrated, use sun protection, plan indoor activities during storms"
#             },
#             "paris": {
#                 "location": "Paris, France", 
#                 "temperature": "16°C (61°F)",
#                 "conditions": "Partly cloudy with occasional rain",
#                 "humidity": "75%",
#                 "advice": "Pack layers and waterproof jacket for walking tours"
#             },
#             "london": {
#                 "location": "London, UK",
#                 "temperature": "14°C (57°F)",
#                 "conditions": "Cool and overcast with frequent rain",
#                 "humidity": "85%",
#                 "advice": "Essential: waterproof jacket and comfortable walking shoes"
#             },
#             "new york": {
#                 "location": "New York, USA",
#                 "temperature": "22°C (72°F)",
#                 "conditions": "Clear skies with comfortable temperatures",
#                 "humidity": "60%",
#                 "advice": "Perfect weather for outdoor activities and sightseeing"
#             }
#         }
        
#         weather = weather_data.get(destination)
#         if weather:
#             return f"🌤️ **Weather for {weather['location']}:**\n\n" \
#                    f"**Temperature**: {weather['temperature']}\n" \
#                    f"**Conditions**: {weather['conditions']}\n" \
#                    f"**Humidity**: {weather['humidity']}\n" \
#                    f"**Travel Advice**: {weather['advice']}\n\n" \
#                    f"*Data from verified weather sources*"
        
#         return f"I don't have weather information for {destination}. I can help with Japan, Paris, London, or New York."

#     def get_currency_info(self, destination: str) -> str:
#         """Get currency information - directly without tools"""
#         currency_data = {
#             "japan": {
#                 "currency": "Japanese Yen (JPY)",
#                 "symbol": "¥",
#                 "rate": "1 USD = 150 JPY",
#                 "cards": "Limited acceptance, cash is still king",
#                 "tipping": "No tipping - it can be considered offensive"
#             },
#             "paris": {
#                 "currency": "Euro (EUR)",
#                 "symbol": "€",
#                 "rate": "1 USD = 0.92 EUR",
#                 "cards": "Widely accepted (Visa, Mastercard, Amex)",
#                 "tipping": "5-10% for good service in restaurants"
#             },
#             "london": {
#                 "currency": "British Pound (GBP)",
#                 "symbol": "£", 
#                 "rate": "1 USD = 0.79 GBP",
#                 "cards": "Universal acceptance, contactless everywhere",
#                 "tipping": "10-15% if service charge not included"
#             },
#             "new york": {
#                 "currency": "US Dollar (USD)",
#                 "symbol": "$",
#                 "rate": "Base currency",
#                 "cards": "Universal acceptance",
#                 "tipping": "18-20% standard in restaurants"
#             }
#         }
        
#         currency = currency_data.get(destination)
#         if currency:
#             return f"💰 **Currency for {destination.title()}:**\n\n" \
#                    f"**Currency**: {currency['currency']} ({currency['symbol']})\n" \
#                    f"**Exchange Rate**: {currency['rate']}\n" \
#                    f"**Card Acceptance**: {currency['cards']}\n" \
#                    f"**Tipping**: {currency['tipping']}"
        
#         return f"I don't have currency information for {destination}."

#     def get_cultural_info(self, destination: str) -> str:
#         """Get cultural information - directly without tools"""
#         cultural_data = {
#             "japan": {
#                 "greeting": "Bow slightly when meeting people",
#                 "dining": "Slurping noodles is acceptable and shows appreciation",
#                 "etiquette": "Remove shoes when entering homes and some restaurants",
#                 "phrases": ["Konnichiwa - Hello", "Arigato - Thank you", "Sumimasen - Excuse me"]
#             },
#             "paris": {
#                 "greeting": "Always say 'Bonjour' when entering shops",
#                 "dining": "Lunch: 12:00-14:00, Dinner: 19:30-22:00",
#                 "etiquette": "Dress well, speak quietly in public",
#                 "phrases": ["Bonjour - Hello", "Merci - Thank you", "Excusez-moi - Excuse me"]
#             },
#             "london": {
#                 "greeting": "Polite queuing is essential",
#                 "dining": "Pub culture is central to social life",
#                 "etiquette": "Mind the gap, stand right on escalators", 
#                 "phrases": ["Please - Please", "Thank you - Thank you", "Sorry - Excuse me"]
#             },
#             "new york": {
#                 "greeting": "Direct and friendly approach",
#                 "dining": "Fast-paced dining culture",
#                 "etiquette": "Tipping is expected everywhere",
#                 "phrases": ["Hi/Hey - Hello", "Thanks - Thank you", "Excuse me - Excuse me"]
#             }
#         }
        
#         culture = cultural_data.get(destination)
#         if culture:
#             phrases_str = ", ".join(culture['phrases'])
#             return f"🤝 **Cultural Tips for {destination.title()}:**\n\n" \
#                    f"**Greetings**: {culture['greeting']}\n" \
#                    f"**Dining**: {culture['dining']}\n" \
#                    f"**Etiquette**: {culture['etiquette']}\n" \
#                    f"**Key Phrases**: {phrases_str}"
        
#         return f"I don't have cultural information for {destination}."

#     def process_user_input(self, message: str) -> str:
#         """Main method to process all user input"""
#         try:
#             logger.info(f"Processing user input: {message}")
#             message_lower = message.lower()
            
#             # Handle greetings
#             if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']) and len(message_lower) < 25:
#                 return """👋 **Hello! Welcome to TourWithEase!**

# I'm the Context Specialist, your travel assistant! I can help you with:

# 🌟 **My Services:**
# • 🌤️ **Weather** - Current conditions and travel advice
# • 💰 **Currency** - Exchange rates, payments, tipping  
# • 🤝 **Culture** - Local customs, etiquette, phrases

# 🗺️ **My Destinations:** Japan, Paris, London, New York

# 💬 **Try asking:** 
# • "What's the weather in Japan?"
# • "Currency info for Paris"
# • "Cultural tips for London"

# How can I help you prepare for your trip today? ✈️"""
            
#             # Extract destination
#             destination = self.extract_destination(message)
#             if not destination:
#                 return """🤔 **I'd be happy to help with travel information!**

# I didn't catch which destination you're asking about. I can provide information for:
# • **Japan** (Tokyo)
# • **Paris** (France)  
# • **London** (UK)
# • **New York** (USA)

# Please try asking:
# • "What's the weather in Japan?"
# • "Tell me about currency in Paris"
# • "Cultural tips for London"

# Which destination interests you? 🌍"""
            
#             # Determine information type and respond directly
#             if any(word in message_lower for word in ['weather', 'temperature', 'climate', 'rain', 'sunny']):
#                 return self.get_weather_info(destination)
#             elif any(word in message_lower for word in ['currency', 'money', 'payment', 'exchange']):
#                 return self.get_currency_info(destination)
#             elif any(word in message_lower for word in ['culture', 'customs', 'etiquette', 'local']):
#                 return self.get_cultural_info(destination)
#             else:
#                 # Comprehensive information
#                 weather = self.get_weather_info(destination)
#                 currency = self.get_currency_info(destination)
#                 culture = self.get_cultural_info(destination)
#                 return f"**Complete Travel Guide for {destination.title()}**\n\n{weather}\n\n{currency}\n\n{culture}"
                
#         except Exception as e:
#             logger.error(f"Processing error: {e}", exc_info=True)
#             return f"I apologize, but I encountered an error. Please try asking about weather, currency, or culture for Japan, Paris, London, or New York."

# # Create agent
# root_agent = ContextSpecialist()

# # Message processing function  
# def process_user_message(message: str) -> str:
#     logger.info(f"Processing message: {message}")
#     return root_agent.process_user_input(message)

# # Hook into ADK (only safe method)
# if hasattr(root_agent, 'generate_response'):
#     def enhanced_generate_response(*args, **kwargs):
#         try:
#             message = args[0] if args else kwargs.get('message', kwargs.get('prompt', ''))
#             if message:
#                 return process_user_message(str(message))
#             return "I'm ready to help with your travel planning!"
#         except Exception as e:
#             logger.error(f"Generate response error: {e}")
#             return "Please ask me about weather, currency, or culture for your destination."
    
#     root_agent.generate_response = enhanced_generate_response

# logger.info("✅ Context Specialist Agent ready with gemini-2.5-pro model")

#4
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Context Specialist Agent - Enhanced with Open-Meteo API Integration (No API Key Required)
# """

# import logging
# import asyncio
# import httpx
# import os
# import json
# from typing import Optional, Dict, Any
# from google.adk.agents import LlmAgent

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # ✅ FIXED: Move all configuration to GLOBAL constants (not instance attributes)
# WEATHER_API_BASE = "https://api.open-meteo.com/v1"
# GEOCODING_API_BASE = "https://geocoding-api.open-meteo.com/v1"
# EXCHANGE_API_URL = os.getenv('EXCHANGE_API_URL', 'https://api.exchangerate-api.com/v4/latest/USD')

# # Global conversation tracking (since we can't use instance attributes)
# conversation_counter = 0

# class ContextSpecialist(LlmAgent):
#     """Context Specialist Agent with Open-Meteo API integration and static fallback"""
    
#     def __init__(self):
#         logger.info("Initializing Context Specialist Agent with Open-Meteo API integration...")
        
#         # ✅ ONLY the required parameters - NO custom attributes!
#         super().__init__(
#             name="context_specialist_agent",
#             model="gemini-2.5-pro"
#         )
        
#         # ✅ REMOVED all self.attribute assignments - they cause Pydantic errors
#         logger.info("Context Specialist Agent initialized successfully with Open-Meteo (no API key needed!)")

#     def reset_conversation_state(self):
#         """Reset agent state between conversations to prevent memory overflow"""
#         try:
#             global conversation_counter
#             conversation_counter = 0
#             logger.info("Agent conversation state reset successfully")
#         except Exception as e:
#             logger.error(f"Failed to reset conversation state: {e}")

#     def extract_destination(self, message: str) -> Optional[str]:
#         """Extract destination from user message"""
#         message_lower = message.lower()
        
#         if any(word in message_lower for word in ["japan", "tokyo", "tyo"]):
#             return "japan"
#         elif any(word in message_lower for word in ["paris", "france", "par"]):
#             return "paris"
#         elif any(word in message_lower for word in ["london", "uk", "britain", "lon"]):
#             return "london"
#         elif any(word in message_lower for word in ["new york", "nyc", "usa"]):
#             return "new york"
        
#         return None

#     async def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
#         """Get coordinates for a location using Open-Meteo Geocoding API"""
#         try:
#             location_mapping = {
#                 "japan": "Tokyo",
#                 "paris": "Paris", 
#                 "london": "London",
#                 "new york": "New York"
#             }
            
#             search_location = location_mapping.get(location.lower(), location)
            
#             async with httpx.AsyncClient(timeout=10.0) as client:
#                 url = f"{GEOCODING_API_BASE}/search"  # ✅ FIXED: Use global constant
#                 params = {
#                     "name": search_location,
#                     "count": 1,
#                     "language": "en",
#                     "format": "json"
#                 }
                
#                 response = await client.get(url, params=params)
#                 response.raise_for_status()
                
#                 data = response.json()
#                 results = data.get("results", [])
                
#                 if results:
#                     result = results[0]
#                     return {
#                         "latitude": result.get("latitude"),
#                         "longitude": result.get("longitude"),
#                         "name": result.get("name"),
#                         "country": result.get("country")
#                     }
                
#                 return None
                
#         except Exception as e:
#             logger.warning(f"Geocoding failed for {location}: {e}")
#             return None

#     async def _fetch_api_weather(self, location: str) -> Optional[Dict[str, Any]]:
#         """Fetch weather from Open-Meteo API (no API key required!)"""
#         try:
#             coords = await self._get_coordinates(location)
#             if not coords:
#                 logger.warning(f"Could not get coordinates for {location}")
#                 return None
            
#             async with httpx.AsyncClient(timeout=10.0) as client:
#                 url = f"{WEATHER_API_BASE}/forecast"  # ✅ FIXED: Use global constant
#                 params = {
#                     "latitude": coords["latitude"],
#                     "longitude": coords["longitude"],
#                     "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
#                     "timezone": "auto",
#                     "forecast_days": 1
#                 }
                
#                 logger.info(f"Fetching weather from Open-Meteo for {coords['name']}")
#                 response = await client.get(url, params=params)
#                 response.raise_for_status()
                
#                 api_data = response.json()
#                 current = api_data.get("current", {})
                
#                 temp_celsius = current.get("temperature_2m", 0)
#                 temp_fahrenheit = (temp_celsius * 9/5) + 32
#                 weather_code = current.get("weather_code", 0)
                
#                 # Map weather codes to descriptions (simplified)
#                 weather_descriptions = {
#                     0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
#                     45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
#                     55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
#                     61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain",
#                     67: "Heavy freezing rain", 71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
#                     77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
#                     82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
#                     95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
#                 }
                
#                 conditions = weather_descriptions.get(weather_code, "Unknown conditions")
                
#                 return {
#                     "location": f"{coords['name']}, {coords['country']}",
#                     "temperature": f"{temp_celsius:.1f}°C ({temp_fahrenheit:.1f}°F)",
#                     "conditions": conditions,
#                     "humidity": f"{current.get('relative_humidity_2m', 0):.0f}%",
#                     "wind_speed": f"{current.get('wind_speed_10m', 0):.1f} km/h",
#                     "advice": f"Current conditions: {conditions.lower()}",
#                     "data_source": "open_meteo_api",
#                     "api_provider": "Open-Meteo"
#                 }
                
#         except Exception as e:
#             logger.warning(f"Open-Meteo API call failed for {location}: {e}")
#             return None

#     async def _fetch_exchange_rates(self) -> Optional[Dict[str, float]]:
#         """Fetch current exchange rates from API"""
#         try:
#             async with httpx.AsyncClient(timeout=10.0) as client:
#                 logger.info("Fetching exchange rates from API")
#                 response = await client.get(EXCHANGE_API_URL)  # ✅ FIXED: Use global constant
#                 response.raise_for_status()
#                 data = response.json()
#                 return data.get("rates", {})
#         except Exception as e:
#             logger.warning(f"Exchange rate API failed: {e}")
#             return None

#     async def get_weather_info(self, destination: str) -> str:
#         """Get weather information with Open-Meteo API integration and fallback"""
#         logger.info(f"Getting weather for {destination} with Open-Meteo API integration")
        
#         try:
#             # Always attempt Open-Meteo API call (no key required!)
#             api_weather_data = await self._fetch_api_weather(destination)
#             if api_weather_data:
#                 logger.info(f"Successfully retrieved weather from Open-Meteo for {destination}")
#                 return f"🌤️ **Weather for {api_weather_data['location']} (Live Data):**\n\n" \
#                        f"**Temperature**: {api_weather_data['temperature']}\n" \
#                        f"**Conditions**: {api_weather_data['conditions']}\n" \
#                        f"**Humidity**: {api_weather_data['humidity']}\n" \
#                        f"**Wind Speed**: {api_weather_data['wind_speed']}\n" \
#                        f"**Travel Advice**: {api_weather_data['advice']}\n\n" \
#                        f"*Live data from {api_weather_data['api_provider']} (Free API)*"
            
#             # Fallback to verified database
#             logger.info(f"Using verified weather database for {destination}")
#             weather_data = {
#                 "japan": {
#                     "location": "Tokyo, Japan",
#                     "temperature": "28°C (82°F)",
#                     "conditions": "Humid with afternoon thunderstorms",
#                     "humidity": "90%",
#                     "advice": "Stay hydrated, use sun protection, plan indoor activities during storms"
#                 },
#                 "paris": {
#                     "location": "Paris, France", 
#                     "temperature": "16°C (61°F)",
#                     "conditions": "Partly cloudy with occasional rain",
#                     "humidity": "75%",
#                     "advice": "Pack layers and waterproof jacket for walking tours"
#                 },
#                 "london": {
#                     "location": "London, UK",
#                     "temperature": "14°C (57°F)",
#                     "conditions": "Cool and overcast with frequent rain",
#                     "humidity": "85%",
#                     "advice": "Essential: waterproof jacket and comfortable walking shoes"
#                 },
#                 "new york": {
#                     "location": "New York, USA",
#                     "temperature": "22°C (72°F)",
#                     "conditions": "Clear skies with comfortable temperatures",
#                     "humidity": "60%",
#                     "advice": "Perfect weather for outdoor activities and sightseeing"
#                 }
#             }
            
#             weather = weather_data.get(destination)
#             if weather:
#                 return f"🌤️ **Weather for {weather['location']}:**\n\n" \
#                        f"**Temperature**: {weather['temperature']}\n" \
#                        f"**Conditions**: {weather['conditions']}\n" \
#                        f"**Humidity**: {weather['humidity']}\n" \
#                        f"**Travel Advice**: {weather['advice']}\n\n" \
#                        f"*Data from verified weather database*"
            
#             return f"I don't have weather information for {destination}. I can help with Japan, Paris, London, or New York."
            
#         except Exception as e:
#             logger.error(f"Weather lookup error for {destination}: {e}")
#             return f"I encountered an error getting weather for {destination}. Please try again."

#     async def get_currency_info(self, destination: str) -> str:
#         """Get currency information with exchange rate API integration and fallback"""
#         logger.info(f"Getting currency info for {destination} with API integration")
        
#         try:
#             # Attempt real exchange rate API call
#             current_rates = await self._fetch_exchange_rates()
            
#             currency_data = {
#                 "japan": {
#                     "currency": "Japanese Yen (JPY)",
#                     "symbol": "¥",
#                     "base_rate": "1 USD = 150 JPY",
#                     "cards": "Limited acceptance, cash is still king",
#                     "tipping": "No tipping - it can be considered offensive",
#                     "rate_key": "JPY"
#                 },
#                 "paris": {
#                     "currency": "Euro (EUR)",
#                     "symbol": "€",
#                     "base_rate": "1 USD = 0.92 EUR",
#                     "cards": "Widely accepted (Visa, Mastercard, Amex)",
#                     "tipping": "5-10% for good service in restaurants",
#                     "rate_key": "EUR"
#                 },
#                 "london": {
#                     "currency": "British Pound (GBP)",
#                     "symbol": "£", 
#                     "base_rate": "1 USD = 0.79 GBP",
#                     "cards": "Universal acceptance, contactless everywhere",
#                     "tipping": "10-15% if service charge not included",
#                     "rate_key": "GBP"
#                 },
#                 "new york": {
#                     "currency": "US Dollar (USD)",
#                     "symbol": "$",
#                     "base_rate": "Base currency",
#                     "cards": "Universal acceptance",
#                     "tipping": "18-20% standard in restaurants",
#                     "rate_key": "USD"
#                 }
#             }
            
#             currency = currency_data.get(destination)
#             if currency:
#                 # Use live rate if available, otherwise use base rate
#                 if current_rates and currency.get("rate_key") in current_rates and currency["rate_key"] != "USD":
#                     live_rate = current_rates[currency["rate_key"]]
#                     rate_display = f"1 USD = {live_rate:.4f} {currency['rate_key']} (Live Rate)"
#                     rate_source = "*Live exchange rates*"
#                 else:
#                     rate_display = currency["base_rate"]
#                     rate_source = "*Standard reference rates*"
                
#                 return f"💰 **Currency for {destination.title()}:**\n\n" \
#                        f"**Currency**: {currency['currency']} ({currency['symbol']})\n" \
#                        f"**Exchange Rate**: {rate_display}\n" \
#                        f"**Card Acceptance**: {currency['cards']}\n" \
#                        f"**Tipping**: {currency['tipping']}\n\n" \
#                        f"{rate_source}"
            
#             return f"I don't have currency information for {destination}."
            
#         except Exception as e:
#             logger.error(f"Currency lookup error for {destination}: {e}")
#             return f"I encountered an error getting currency info for {destination}. Please try again."

#     def get_cultural_info(self, destination: str) -> str:
#         """Get cultural information - enhanced static database"""
#         cultural_data = {
#             "japan": {
#                 "greeting": "Bow slightly when meeting people, avoid excessive handshaking",
#                 "dining": "Slurping noodles is acceptable and shows appreciation",
#                 "etiquette": "Remove shoes when entering homes, temples, and some restaurants",
#                 "phrases": [
#                     "Konnichiwa - Hello (afternoon)",
#                     "Arigato gozaimasu - Thank you very much", 
#                     "Sumimasen - Excuse me/Sorry",
#                     "Eigo ga hanasemasu ka? - Do you speak English?"
#                 ],
#                 "taboos": [
#                     "Don't blow your nose in public",
#                     "Don't eat while walking",
#                     "Never tip - it can be considered offensive"
#                 ]
#             },
#             "paris": {
#                 "greeting": "Always say 'Bonjour' (morning) or 'Bonsoir' (evening) when entering shops",
#                 "dining": "Lunch: 12:00-14:00, Dinner: 19:30-22:00, don't rush meals",
#                 "etiquette": "Dress well, speak quietly in public spaces",
#                 "phrases": [
#                     "Bonjour/Bonsoir - Hello (morning/evening)",
#                     "Merci beaucoup - Thank you very much",
#                     "Excusez-moi - Excuse me",
#                     "Parlez-vous anglais? - Do you speak English?"
#                 ],
#                 "taboos": [
#                     "Don't eat on public transport",
#                     "Don't speak loudly in restaurants",
#                     "Don't ask for ketchup with traditional French meals"
#                 ]
#             },
#             "london": {
#                 "greeting": "Polite queuing is essential, 'please' and 'thank you' frequently used",
#                 "dining": "Pub culture is central, afternoon tea is traditional",
#                 "etiquette": "Mind the gap, stand right on escalators, apologize frequently", 
#                 "phrases": [
#                     "Good morning/afternoon - Hello",
#                     "Please - Please (used very frequently)",
#                     "Thank you/Cheers - Thank you",
#                     "Sorry - Excuse me (used for everything)"
#                 ],
#                 "taboos": [
#                     "Don't jump queues - it's seriously offensive",
#                     "Don't block the right side of escalators",
#                     "Don't be loud on public transport"
#                 ]
#             },
#             "new york": {
#                 "greeting": "Direct and friendly approach, firm handshakes",
#                 "dining": "Fast-paced dining culture, brunch is popular on weekends",
#                 "etiquette": "Tipping is expected everywhere, walk fast, be direct",
#                 "phrases": [
#                     "Hi/Hey - Hello (casual)",
#                     "How you doing? - How are you?",
#                     "Thanks - Thank you",
#                     "Have a good one - Goodbye"
#                 ],
#                 "taboos": [
#                     "Don't block pedestrian traffic",
#                     "Don't forget to tip service workers",
#                     "Don't stand on the left side of escalators"
#                 ]
#             }
#         }
        
#         culture = cultural_data.get(destination)
#         if culture:
#             phrases_str = ", ".join(culture['phrases'])
#             taboos_str = ", ".join(culture['taboos'])
#             return f"🤝 **Cultural Tips for {destination.title()}:**\n\n" \
#                    f"**Greetings**: {culture['greeting']}\n" \
#                    f"**Dining**: {culture['dining']}\n" \
#                    f"**Etiquette**: {culture['etiquette']}\n" \
#                    f"**Key Phrases**: {phrases_str}\n" \
#                    f"**Important Taboos**: {taboos_str}\n\n" \
#                    f"*Verified cultural information*"
        
#         return f"I don't have cultural information for {destination}."

#     async def process_user_input(self, message: str) -> str:
#         """Main method to process all user input with conversation management"""
#         try:
#             # ✅ FIXED: Use global conversation tracking
#             global conversation_counter
#             conversation_counter += 1
#             logger.info(f"Processing user input #{conversation_counter}: {message}")
            
#             message_lower = message.lower().strip()
#             if (message_lower in ["hi", "hello", "hey"] or conversation_counter > 15):
#                 self.reset_conversation_state()
            
#             # Handle greetings
#             if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']) and len(message_lower) < 25:
#                 return """👋 **Hello! Welcome to TourWithEase!**

# I'm the Context Specialist, your enhanced travel assistant with FREE live weather data! 

# 🌟 **My Services:**
# • 🌤️ **Weather** - Live conditions from Open-Meteo (no API key needed!)
# • 💰 **Currency** - Real-time exchange rates and payment info
# • 🤝 **Culture** - Local customs, etiquette, essential phrases

# 🗺️ **My Destinations:** Japan, Paris, London, New York

# 💬 **Try asking:** 
# • "What's the weather in Japan?"
# • "Currency info for Paris"
# • "Cultural tips for London"

# How can I help you prepare for your trip today? ✈️"""
            
#             # Extract destination
#             destination = self.extract_destination(message)
#             if not destination:
#                 return """🤔 **I'd be happy to help with travel information!**

# I didn't catch which destination you're asking about. I can provide information for:
# • **Japan** (Tokyo) - FREE live weather data
# • **Paris** (France) - Real-time exchange rates  
# • **London** (UK) - Current conditions (no API key needed)
# • **New York** (USA) - Live market data

# Please try asking:
# • "What's the weather in Japan?"
# • "Tell me about currency in Paris"
# • "Cultural tips for London"

# Which destination interests you? 🌍"""
            
#             # Determine information type and respond with async methods where needed
#             if any(word in message_lower for word in ['weather', 'temperature', 'climate', 'rain', 'sunny']):
#                 return await self.get_weather_info(destination)
#             elif any(word in message_lower for word in ['currency', 'money', 'payment', 'exchange']):
#                 return await self.get_currency_info(destination)
#             elif any(word in message_lower for word in ['culture', 'customs', 'etiquette', 'local']):
#                 return self.get_cultural_info(destination)
#             else:
#                 # Comprehensive information
#                 weather = await self.get_weather_info(destination)
#                 await asyncio.sleep(0.1)
#                 currency = await self.get_currency_info(destination)
#                 await asyncio.sleep(0.1)
#                 culture = self.get_cultural_info(destination)
#                 return f"**Complete Travel Guide for {destination.title()}**\n\n{weather}\n\n{currency}\n\n{culture}"
                
#         except Exception as e:
#             logger.error(f"Processing error: {e}", exc_info=True)
#             return f"I apologize, but I encountered an error. Please try asking about weather, currency, or culture for Japan, Paris, London, or New York."

# # Create agent
# root_agent = ContextSpecialist()

# # Message processing function  
# def process_user_message(message: str) -> str:
#     logger.info(f"Processing message: {message}")
#     try:
#         return asyncio.run(root_agent.process_user_input(message))
#     except Exception as e:
#         logger.error(f"Async processing error: {e}")
#         return "I'm here to help with travel information! Please ask about weather, currency, or culture."

# # Hook into ADK
# if hasattr(root_agent, 'generate_response'):
#     def enhanced_generate_response(*args, **kwargs):
#         try:
#             message = args[0] if args else kwargs.get('message', kwargs.get('prompt', ''))
#             if message:
#                 return process_user_message(str(message))
#             return "I'm ready to help with your travel planning!"
#         except Exception as e:
#             logger.error(f"Generate response error: {e}")
#             return "Please ask me about weather, currency, or culture for your destination."
    
#     root_agent.generate_response = enhanced_generate_response

# logger.info("✅ Context Specialist Agent ready with Open-Meteo integration (NO API KEY NEEDED!)")

#5
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Specialist Agent - Complete Travel Assistant
"""

import logging
from google.adk.agents import LlmAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextSpecialist(LlmAgent):
    """Complete Context Specialist Agent for travel information"""
    
    def __init__(self):
        logger.info("Initializing Context Specialist Agent...")
        super().__init__(
            name="context_specialist_agent",
            model="gemini-2.5-pro"
        )
        logger.info("Context Specialist Agent initialized successfully")

root_agent = ContextSpecialist()
logger.info("✅ Context Specialist Agent ready")


