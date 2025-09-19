# import asyncio
# import os
# import logging
# from typing import Dict, Any, Optional, List
# # Assuming base_agent.py contains the definitions for ADKAgent, Memory, A2AMessage, Tool
# from base_agent import ADKAgent, Memory, A2AMessage, Tool
# from dotenv import load_dotenv

# load_dotenv()

# class AWSLambdaTool(Tool):
#     """Base class for AWS Lambda integration tools"""
#     def __init__(self, name: str, description: str, endpoint: str, api_key: str = None):
#         super().__init__(name, description)
#         self.endpoint = endpoint
#         self.api_key = api_key or os.getenv('AWS_API_KEY')
#         self.base_url = os.getenv('AWS_API_GATEWAY_URL')

#     async def _call_lambda(self, payload: Dict[str, Any]) -> Dict[str, Any]:
#         """Make HTTP call to AWS Lambda via API Gateway"""

#         headers = {
#             'Content-Type': 'application/json'
#         }

#         if self.api_key:
#             headers['x-api-key'] = self.api_key
#         url = f"{self.base_url}/{self.endpoint}"

#         async with httpx.AsyncClient(timeout=30.0) as client:
#             response = await client.post(url, json=payload, headers=headers)
#             response.raise_for_status()
#             return response.json()

# class FlightSearchTool(AWSLambdaTool):
#     """Tool for searching flights via AWS Lambda"""
#     def __init__(self):
#         super().__init__(
#             name="flight_search",
#             description="Search for flights using Amadeus GDS via AWS Lambda",
#             endpoint="search"
#             # endpoint="flight-search"
#         )
    
#     async def execute(self, origin: str, destination: str, departure_date: str, return_date: str = None, adults: int, children: int, infants: int, cabin_class: str , currency_code: str) -> Dict[str, Any]:
#     """Execute flight search"""
#         # FIX: This payload now matches the structure your Lambda function expects.
#         payload = {
#             "originLocationCode": origin,
#             "destinationLocationCode": destination,
#             "departureDate": departure_date,
#             "returnDate": return_date,
#             "adults": str(adults),
#             "children": str(children),
#             "infants": str(infants),
#             "max": "100",  # Using a default max value as specified
#             "currencyCode": currency_code,
#             "travelClass": cabin_class
#         }
#         try:
#             result = await self._call_lambda(payload)
#             return {
#                 "status": "success",
#                 "flights": result.get("flights", []),
#                 "search_criteria": payload
#             }

#         except Exception as e:
#             return {
#                 "status": "error",
#                 "message": str(e),
#                 "search_criteria": payload
#             }


#     # async def execute(self, origin: str, destination: str, departure_date:
#     # str, return_date: str = None, passengers: int = 1, cabin_class: str =
#     # "ECONOMY") -> Dict[str, Any]:
#     #     """Execute flight search"""

#     #     payload = {
#     #         "origin": origin,
#     #         "destination": destination,
#     #         "departure_date": departure_date,
#     #         "return_date": return_date,
#     #         "passengers": passengers,
#     #         "cabin_class": cabin_class
#     #     }

#     #     try:
#     #         result = await self._call_lambda(payload)
#     #         return {
#     #             "status": "success",
#     #             "flights": result.get("flights", []),
#     #             "search_criteria": payload
#     #         }

#     #     except Exception as e:
#     #         return {
#     #             "status": "error",
#     #             "message": str(e),
#     #             "search_criteria": payload
#     #         }
            
# class PriceAnalysisTool(Tool):
#     """Tool for analyzing prices and providing insights"""
#     def __init__(self):
#         super().__init__(
#             name="price_analysis",
#             description="Analyze travel prices and provide insights"
#         )

#     async def execute(self, options: List[Dict[str, Any]], criteria: Dict[str, Any]) -> Dict[str, Any]:
#         """Analyze price options"""
#         if not options:
#             return {"status": "no_data", "message": "No options to analyze"}

#         # Simple price analysis
#         prices = [float(option.get("price", 0)) for option in options if "price" in option]

#         if not prices:
#             return {"status": "no_prices", "message": "No price data available"}
#             analysis = {
#                 "status": "success",
#                 "price_range": {
#                     "min": min(prices),
#                     "max": max(prices),
#                     "average": sum(prices) / len(prices)
#                 },
#                 "recommendations": []
#             }

#             # Add recommendations based on price analysis
#             min_price_idx = prices.index(min(prices))
#             analysis["recommendations"].append({
#                 "type": "best_value",
#                 "option_index": min_price_idx,
#                 "reason": "Lowest price option"
#             })

#             # Find middle-priced option

#             sorted_prices = sorted(enumerate(prices), key=lambda x: x[1])
#             mid_idx = sorted_prices[len(sorted_prices)//2][0]
#             analysis["recommendations"].append({
#                 "type": "balanced",
#                 "option_index": mid_idx,
#                 "reason": "Good balance of price and options"
#             })

#             return analysis

# class FlightSpecialist(ADKAgent):
#     """Specialized agent for flight-related operations"""
#     def __init__(self):
#         tools = [FlightSearchTool(), PriceAnalysisTool()]
#         super().__init__(
#             model="gemini-2.5-flash",
#             name="flight-specialist",
#             description="Expert in flight searches, bookings, and price analysis",
#             tools=tools,
#             memory=Memory(memory_type="conversation_buffer", k=10),
#             instruction="You are an agent to help answer users' various questions."
#         )
        
#         self.logger.info(f"FlightSpecialist agent '{self.name}'.")
        
#     async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
#         """Process direct flight requests"""
#         action = request.get("action", "search")
#         params = request.get("parameters", {})
#         self.logger.debug(f"Processing direct request: action='{action}', params={params}") # Added debug log
        
#         if action == "search_flights":
#             return await self._search_flights(params)
#         elif action == "analyze_prices":
#             return await self._analyze_prices(params)
#         else:
#             self.logger.warning(f"Received unknown action in process_request: {action}") # Added warning log
#             return {
#                 "status": "error",
#                 "message": f"Unknown action: {action}"
#             }

#     async def process_a2a_request(self, message: A2AMessage) -> Dict[str, Any]:
#         """Handle A2A requests from other agents"""
#         payload = message.payload
#         action = payload.get("action")
#         parameters = payload.get("parameters", {})
#         self.logger.info(f"Processing A2A request: {action} from {message.from_agent} with params={parameters}")
#         self.logger.info(f"Processing A2A request: {action} from {message.from_agent}")
        
#         if action == "search_flights":
#             result = await self._search_flights(parameters)
#             self.logger.debug(f"A2A search_flights result: {result.get('status')}")
#             return result
#         elif action == "analyze_prices":
#             result = await self._analyze_prices(parameters)
#             self.logger.debug(f"A2A analyze_prices result: {result.get('status')}")
#             return result
#         else:
#             self.logger.warning(f"Received unknown action in process_a2a_request: {action}")
#             return {
#                 "status": "error",
#                 "message": f"Unknown action: {action}",
#                 "supported_actions": ["search_flights", "analyze_prices"]
#             }

#     async def _search_flights(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Search for flights using AWS Lambda"""
#         self.logger.info(f"Initiating flight search with parameters: {params}")
#         try:
#             # Extract parameters
#             origin = params.get("origin", "NYC")
#             destination = params.get("destination", "PAR")
#             departure_date = params.get("departure_date")
#             return_date = params.get("return_date")
#             passengers = params.get("passengers", 1)
#             cabin_class = params.get("cabin_class", "ECONOMY")
#             trip_type = params.get("trip_type", "leisure")
            
#             self.logger.debug(f"Calling 'flight_search' tool for {origin} to {destination} on {departure_date}")

#             # Use flight search tool
#             search_result = await self.use_tool(
#                 "flight_search",
#                 origin=origin,
#                 destination=destination,
#                 departure_date=departure_date,
#                 return_date=return_date,
#                 passengers=passengers,
#                 cabin_class=cabin_class
#             )
            
#             self.logger.debug(f"Flight search tool returned status: {search_result.get('status')}")
            
#             if search_result["status"] == "success":
#                 flights = search_result["flights"]
#                 self.logger.info(f"Found {len(flights)} flights from {origin} to {destination}.")
#                 # Enhance results based on trip type
#                 if trip_type == "romantic":
#                     # Prefer evening flights, premium airlines
#                     flights = self._prioritize_romantic_flights(flights)
#                 elif trip_type == "business":
#                     # Prefer convenient times, premium airlines
#                     flights = self._prioritize_business_flights(flights)

#                 # Add price analysis
#                 if len(flights) > 1:
#                     self.logger.debug(f"Calling 'price_analysis' tool for {len(flights)} options.") # Debug before tool call
#                     price_analysis = await self.use_tool(
#                         "price_analysis",
#                         options=flights,
#                         criteria=params
#                     )
#                     self.logger.debug(f"Price analysis tool returned status: {price_analysis.get('status')}") # Debug after tool call
#                     search_result["price_analysis"] = price_analysis
                
#                 # Store search in memory
#                 self.memory.add_message(
#                     "system",
#                     f"Searched flights {origin} to {destination} on {departure_date}, found {len(flights)} options"
#                 )
                
#             return search_result

#         except Exception as e:
#             self.logger.error(f"Flight search error: {e}", exc_info=True) # Log exception details
#             return {
#                 "status": "error",
#                 "message": f"Flight search failed: {str(e)}",
#                 "parameters": params
#             }

#     async def _analyze_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Analyze flight prices"""
#         self.logger.info(f"Initiating price analysis with parameters: {params}") # Added info log
#         try:
#             options = params.get("options", [])
#             criteria = params.get("criteria", {})
            
#             self.logger.debug(f"Calling 'price_analysis' tool for {len(options)} options.") # Debug before tool call
#             price_analysis = await self.use_tool(
#                 "price_analysis",
#                 options=options,
#                 criteria=criteria
#             )
#             self.logger.debug(f"Price analysis tool returned status: {price_analysis.get('status')}") # Debug after tool call
            
#             self.memory.add_message(
#                 "system",
#                 f"Analyzed {len(options)} flight options for price comparison"
#             )
            
#             return price_analysis

#         except Exception as e:
#             self.logger.error(f"Price analysis error: {e}", exc_info=True) # Log exception details
#             return {
#                 "status": "error",
#                 "message": f"Price analysis failed: {str(e)}",
#                 "parameters": params
#             }

#     def _prioritize_romantic_flights(self, flights: list) -> list:
#         """Prioritize flights suitable for romantic trips"""
#         # Sort by departure time (prefer evening flights) and airline quality
#         self.logger.debug("Prioritizing flights for romantic trip.")
#         def romantic_score(flight):
#             score = 0
#             departure_time = flight.get("departure_time", "")
#             if "18:" in departure_time or "19:" in departure_time or "20:" in departure_time:
#                 score += 3  # Evening flights
#             if flight.get("airline") in ["Emirates", "Qatar Airways", "Singapore Airlines"]:
#                 score += 2  # Premium airlines
#             if flight.get("cabin_class") in ["BUSINESS", "FIRST"]:
#                 score += 1  # Premium cabins
#             return score
        
#         return sorted(flights, key=romantic_score, reverse=True)

#     def _prioritize_business_flights(self, flights: list) -> list:
#         """Prioritize flights suitable for business trips"""
#         # Sort by convenience and airline reliability
#         self.logger.debug("Prioritizing flights for business trip.")
#         def business_score(flight):
#             score = 0
#             departure_time = flight.get("departure_time", "")
#             # Prefer morning or early afternoon flights
#             if any(time in departure_time for time in ["08:", "09:", "10:", "13:", "14:"]):
#                 score += 3
#             if flight.get("airline") in ["American Airlines", "Delta", "United", "Lufthansa"]:
#                 score += 2  # Business-friendly airlines
#             if flight.get("cabin_class") == "BUSINESS":
#                 score += 1
#             if flight.get("duration_minutes", 999) < 480:  # Under 8 hours
#                 score += 1
#             return score
        
#         return sorted(flights, key=business_score, reverse=True)

#v2
# flight_specialist_agent.py
# """
# Flight Specialist Agent - ADK/A2A Implementation
# Handles flight search, pricing, and booking via Amadeus GDS integration
# AWS serverless API Gateway → Lambda proxy integration (500/s rate limit)
# """

# import asyncio
# import aiohttp
# import json
# import logging
# from typing import Dict, List, Optional, Any
# from datetime import datetime, timedelta
# from dataclasses import dataclass
# from vertexai.generative_models import GenerativeModel

# logger = logging.getLogger(__name__)

# @dataclass
# class FlightSearchParams:
#     """Flight search parameters with validation"""
#     origin_location_code: str
#     destination_location_code: str
#     departure_date: str
#     adults: int
#     return_date: Optional[str] = None
#     children: Optional[int] = None
#     infant: Optional[int] = None
#     travel_class: Optional[str] = "ECONOMY"

# class FlightSpecialistAgent:
#     """
#     Flight Operations Specialist Agent
#     Personality: respectful, friendly, proactive, detail-oriented
#     Communication: professional advisory with layman-friendly technical translation
#     """
    
#     def __init__(self, config: Dict, security_module):
#         """
#         Initialize Flight Specialist Agent with AWS serverless integration
        
#         Args:
#             config: System configuration dictionary
#             security_module: Security guardrails instance
#         """
#         self.config = config
#         self.security_module = security_module
#         self.agent_config = config['agents']['flight_specialist']
#         self.api_config = config['api_integration']['amadeus_gds']
        
#         # Initialize Gemini model for conversational capabilities
#         self.model = GenerativeModel("gemini-2.5-pro")
#         self.llm_config = config['llm_config']['parameters']
        
#         # Session management for conversational flow
#         self.active_sessions = {}
        
#         logger.info("Flight Specialist Agent initialized")

#     async def process_request(self, user_input: str, session_id: str) -> Any:
#         """
#         Main request processing with structured conversational flow
        
#         Args:
#             user_input: User query/request
#             session_id: Unique session identifier
            
#         Returns:
#             AgentResponse: Structured response with flight data or guidance
#         """
#         logger.info(f"Flight Specialist processing request for session {session_id}")
        
#         try:
#             # Get or create session context
#             session_context = self._get_session_context(session_id)
            
#             # Determine current conversation stage
#             conversation_stage = self._determine_conversation_stage(session_context)
            
#             # Process based on conversation stage
#             if conversation_stage == "greeting":
#                 response = await self._handle_greeting(user_input, session_id)
#             elif conversation_stage == "requirements_collection":
#                 response = await self._collect_flight_requirements(user_input, session_id)
#             elif conversation_stage == "flight_search":
#                 response = await self._execute_flight_search(session_id)
#             elif conversation_stage == "flight_analysis":
#                 response = await self._analyze_flight_options(user_input, session_id)
#             elif conversation_stage == "booking_process":
#                 response = await self._handle_booking_process(user_input, session_id)
#             else:
#                 response = await self._handle_general_flight_query(user_input, session_id)
            
#             # Update session context
#             self._update_session_context(session_id, response)
            
#             return response
            
#         except Exception as e:
#             logger.error(f"Flight Specialist request processing failed: {e}")
#             return self._create_error_response(str(e), session_id)

#     def _get_session_context(self, session_id: str) -> Dict:
#         """Retrieve or create session context for conversation continuity"""
        
#         if session_id not in self.active_sessions:
#             self.active_sessions[session_id] = {
#                 "stage": "greeting",
#                 "collected_data": {},
#                 "flight_preferences": {},
#                 "search_results": [],
#                 "conversation_history": [],
#                 "created_at": datetime.now()
#             }
#             logger.debug(f"Created new session context for {session_id}")
        
#         return self.active_sessions[session_id]

#     async def _handle_greeting(self, user_input: str, session_id: str) -> Dict:
#         """
#         Handle initial greeting and capability overview
#         Structured conversational script flow as per specification
#         """
        
#         greeting_message = self.config['core_settings']['greeting_message']
        
#         # Personalized greeting with capability explanation
#         prompt = f"""
#         As the Flight Specialist in the MAF system, provide a warm greeting and overview of capabilities.
        
#         Base greeting: {greeting_message}
        
#         User message: {user_input}
        
#         Explain flight capabilities in layman terms:
#         - Flight search across global routes
#         - Real-time pricing and availability 
#         - Flight booking and order creation
#         - Airport and city code lookup
#         - Price analysis and recommendations
        
#         Ask what specific flight assistance they need and guide them through the process.
#         Be friendly, professional, and proactive.
#         """
        
#         try:
#             response = await self.model.generate_content_async(
#                 prompt, 
#                 generation_config=self.llm_config
#             )
            
#             return {
#                 "agent_id": "flight_specialist",
#                 "success": True,
#                 "data": {
#                     "message": response.text,
#                     "next_step": "requirements_collection",
#                     "capabilities": [
#                         "flight_search", "flight_pricing", "flight_booking", 
#                         "airport_lookup", "price_analysis"
#                     ]
#                 },
#                 "metadata": {"stage": "greeting_complete"},
#                 "timestamp": datetime.now()
#             }
            
#         except Exception as e:
#             logger.error(f"Greeting handling failed: {e}")
#             return self._create_error_response(str(e), session_id)

#     async def _collect_flight_requirements(self, user_input: str, session_id: str) -> Dict:
#         """
#         Collect flight requirements with technical translation to layman terms
#         Ensures payload completeness for Amadeus GDS API calls
#         """
        
#         session_context = self.active_sessions[session_id]
#         collected_data = session_context.get("collected_data", {})
        
#         # Analyze user input to extract flight parameters
#         extracted_params = await self._extract_flight_parameters(user_input)
        
#         # Update collected data
#         collected_data.update(extracted_params)
#         session_context["collected_data"] = collected_data
        
#         # Check completeness of required parameters
#         required_fields = self.agent_config['guardrails']['parameter_validation']['required_fields']
#         missing_fields = []
        
#         for field in required_fields:
#             # Map display names to API parameter names
#             api_field = self._map_to_api_field(field)
#             if api_field not in collected_data or not collected_data[api_field]:
#                 missing_fields.append(field)
        
#         if missing_fields:
#             # Request missing information in layman terms
#             response = await self._request_missing_information(missing_fields, collected_data, session_id)
#         else:
#             # All required data collected, proceed to search
#             response = await self._confirm_search_parameters(collected_data, session_id)
#             session_context["stage"] = "flight_search"
        
#         return response

#     async def _extract_flight_parameters(self, user_input: str) -> Dict:
#         """
#         Extract flight parameters from natural language input
#         Handles technical translation from layman terms to API parameters
#         """
        
#         prompt = f"""
#         Extract flight search parameters from this user input: "{user_input}"
        
#         Map to these API parameters:
#         - originLocationCode (3-letter airport code)
#         - destinationLocationCode (3-letter airport code) 
#         - departureDate (YYYY-MM-DD format)
#         - adults (number of adult passengers)
#         - returnDate (YYYY-MM-DD format, optional)
#         - children (number of child passengers, optional)
#         - infant (number of infant passengers, optional)
#         - travelClass (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
        
#         Valid airport codes (from technical specifications): {self.config['test_data']['valid_airport_codes']}
        
#         Return as JSON with extracted parameters, or empty dict if none found.
#         Only use airport codes from the valid list above.
#         """
        
#         try:
#             response = await self.model.generate_content_async(
#                 prompt,
#                 generation_config=self.llm_config
#             )
            
#             # Parse JSON response
#             extracted_data = json.loads(response.text)
            
#             # Validate extracted airport codes against security module
#             if 'originLocationCode' in extracted_data:
#                 if not self.security_module.validate_airport_code(extracted_data['originLocationCode']):
#                     del extracted_data['originLocationCode']
            
#             if 'destinationLocationCode' in extracted_data:
#                 if not self.security_module.validate_airport_code(extracted_data['destinationLocationCode']):
#                     del extracted_data['destinationLocationCode']
            
#             logger.debug(f"Extracted flight parameters: {extracted_data}")
#             return extracted_data
            
#         except Exception as e:
#             logger.error(f"Parameter extraction failed: {e}")
#             return {}

#     async def _execute_flight_search(self, session_id: str) -> Dict:
#         """
#         Execute flight search via AWS serverless API Gateway → Lambda integration
#         Rate limit: 500/s as per specification
#         """
        
#         session_context = self.active_sessions[session_id]
#         search_params = session_context["collected_data"]
        
#         # Construct API endpoint URL
#         # base_url = self.api_config['base_url']
#         # environment = self.api_config['environment'] 
#         endpoint = "https://r9kpch95c6.execute-api.ap-southeast-2.amazonaws.com/test/flights/search"
        
#         # Prepare query parameters
#         query_params = {
#             'adults': search_params.get('adults', 1),
#             'originLocationCode': search_params.get('originLocationCode'),
#             'destinationLocationCode': search_params.get('destinationLocationCode'),
#             'departureDate': search_params.get('departureDate'),
#         }
        
#         # Add optional parameters if present
#         if search_params.get('returnDate'):
#             query_params['returnDate'] = search_params['returnDate']
#         if search_params.get('children'):
#             query_params['children'] = search_params['children']
#         if search_params.get('infant'):
#             query_params['infant'] = search_params['infant']
#         if search_params.get('travelClass'):
#             query_params['travelClass'] = search_params['travelClass']
        
#         logger.info(f"Executing flight search with parameters: {query_params}")
        
#         try:
#             # Make API call to AWS serverless backend
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(
#                     endpoint, 
#                     params=query_params,
#                     timeout=aiohttp.ClientTimeout(total=30)
#                 ) as response:
                    
#                     if response.status == 200:
#                         flight_data = await response.json()
                        
#                         # Store search results in session context
#                         self.active_sessions[session_id]["search_results"] = flight_data
#                         self.active_sessions[session_id]["stage"] = "flight_analysis"
                        
#                         # Translate technical response to user-friendly format
#                         user_friendly_response = await self._translate_flight_results(flight_data)
                        
#                         return {
#                             "agent_id": "flight_specialist",
#                             "success": True,
#                             "data": {
#                                 "message": user_friendly_response,
#                                 "flight_offers": flight_data.get('data', {}).get('flightOffers', []),
#                                 "results_count": len(flight_data.get('data', {}).get('flightOffers', [])),
#                                 "next_step": "flight_analysis"
#                             },
#                             "metadata": {"stage": "search_complete", "api_response": "success"},
#                             "timestamp": datetime.now()
#                         }
#                     else:
#                         error_msg = f"API request failed with status {response.status}"
#                         logger.error(error_msg)
#                         return self._create_error_response(error_msg, session_id)
                        
#         except asyncio.TimeoutError:
#             error_msg = "Flight search request timed out"
#             logger.error(error_msg)
#             return self._create_error_response(error_msg, session_id)
#         except Exception as e:
#             error_msg = f"Flight search failed: {str(e)}"
#             logger.error(error_msg)
#             return self._create_error_response(error_msg, session_id)

#     async def _translate_flight_results(self, flight_data: Dict) -> str:
#         """
#         Translate technical flight API response to user-friendly format
#         Heavy lifting of technical translation to layman terms as per specification
#         """
        
#         flight_offers = flight_data.get('data', {}).get('flightOffers', [])
        
#         if not flight_offers:
#             return "No flights found for your search criteria. Please try different dates or destinations."
        
#         # Prepare context for Gemini translation
#         prompt = f"""
#         Translate this flight search results into user-friendly format:
        
#         Flight offers count: {len(flight_offers)}
        
#         Sample flight data: {json.dumps(flight_offers[:2], indent=2)}
        
#         Create a helpful summary that includes:
#         1. Number of flight options found
#         2. Price range overview
#         3. Brief description of top 3 options with:
#            - Airlines and flight numbers in simple terms
#            - Departure and arrival times
#            - Duration and stops
#            - Price information
#         4. Guidance on next steps (analysis, booking, modifications)
        
#         Use friendly, professional language. Avoid technical jargon.
#         Explain any airline codes, airport codes, or technical terms.
#         """
        
#         try:
#             response = await self.model.generate_content_async(
#                 prompt,
#                 generation_config=self.llm_config
#             )
            
#             return response.text
            
#         except Exception as e:
#             logger.error(f"Flight results translation failed: {e}")
#             return f"Found {len(flight_offers)} flight options. Technical details are available for review."

#     def _map_to_api_field(self, display_field: str) -> str:
#         """Map user-friendly field names to API parameter names"""
#         field_mapping = {
#             'originLocationCode': 'originLocationCode',
#             'destinationLocationCode': 'destinationLocationCode', 
#             'departureDate': 'departureDate',
#             'adults': 'adults',
#             'returnDate': 'returnDate',
#             'children': 'children',
#             'infant': 'infant',
#             'travelClass': 'travelClass'
#         }
        
#         return field_mapping.get(display_field, display_field)

#     def _create_error_response(self, error_message: str, session_id: str) -> Dict:
#         """Create standardized error response for A2A communication"""
#         return {
#             "agent_id": "flight_specialist",
#             "success": False,
#             "data": {},
#             "metadata": {"error": error_message, "session_id": session_id},
#             "timestamp": datetime.now(),
#             "errors": [error_message]
#         }

#     # Additional methods for booking process, price analysis, etc.
#     # ... (Implementation continues with remaining flight operations)
#     async def _analyze_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
#         """Analyze flight prices"""
#         self.logger.info(f"Initiating price analysis with parameters: {params}") # Added info log
#         try:
#             options = params.get("options", [])
#             criteria = params.get("criteria", {})
            
#             self.logger.debug(f"Calling 'price_analysis' tool for {len(options)} options.") # Debug before tool call
#             price_analysis = await self.use_tool(
#                 "price_analysis",
#                 options=options,
#                 criteria=criteria
#             )
#             self.logger.debug(f"Price analysis tool returned status: {price_analysis.get('status')}") # Debug after tool call
            
#             self.memory.add_message(
#                 "system",
#                 f"Analyzed {len(options)} flight options for price comparison"
#             )
            
#             return price_analysis

#         except Exception as e:
#             self.logger.error(f"Price analysis error: {e}", exc_info=True) # Log exception details
#             return {
#                 "status": "error",
#                 "message": f"Price analysis failed: {str(e)}",
#                 "parameters": params
#             }

#     def _prioritize_romantic_flights(self, flights: list) -> list:
#         """Prioritize flights suitable for romantic trips"""
#         # Sort by departure time (prefer evening flights) and airline quality
#         self.logger.debug("Prioritizing flights for romantic trip.")
#         def romantic_score(flight):
#             score = 0
#             departure_time = flight.get("departure_time", "")
#             if "18:" in departure_time or "19:" in departure_time or "20:" in departure_time:
#                 score += 3  # Evening flights
#             if flight.get("airline") in ["Emirates", "Qatar Airways", "Singapore Airlines"]:
#                 score += 2  # Premium airlines
#             if flight.get("cabin_class") in ["BUSINESS", "FIRST"]:
#                 score += 1  # Premium cabins
#             return score
        
#         return sorted(flights, key=romantic_score, reverse=True)

#     def _prioritize_business_flights(self, flights: list) -> list:
#         """Prioritize flights suitable for business trips"""
#         # Sort by convenience and airline reliability
#         self.logger.debug("Prioritizing flights for business trip.")
#         def business_score(flight):
#             score = 0
#             departure_time = flight.get("departure_time", "")
#             # Prefer morning or early afternoon flights
#             if any(time in departure_time for time in ["08:", "09:", "10:", "13:", "14:"]):
#                 score += 3
#             if flight.get("airline") in ["American Airlines", "Delta", "United", "Lufthansa"]:
#                 score += 2  # Business-friendly airlines
#             if flight.get("cabin_class") == "BUSINESS":
#                 score += 1
#             if flight.get("duration_minutes", 999) < 480:  # Under 8 hours
#                 score += 1
#             return score
        
#         return sorted(flights, key=business_score, reverse=True)

#v3
# flight_specialist_agent.py
# flight_specialist_agent.py
"""
Flight Specialist Agent - ADK/A2A Implementation
Handles flight search, pricing, and booking via Amadeus GDS integration
AWS serverless API Gateway → Lambda proxy integration (500/s rate limit)
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from vertexai.generative_models import GenerativeModel

logger = logging.getLogger(__name__)

@dataclass
class FlightSearchParams:
    """Flight search parameters with validation"""
    origin_location_code: str
    destination_location_code: str
    departure_date: str
    adults: int
    return_date: Optional[str] = None
    children: Optional[int] = None
    infant: Optional[int] = None
    travel_class: Optional[str] = "ECONOMY"

class FlightSpecialistAgent:
    """
    Flight Operations Specialist Agent
    Personality: respectful, friendly, proactive, detail-oriented
    Communication: professional advisory with layman-friendly technical translation
    """
    
    def __init__(self, config: Dict, security_module):
        """
        Initialize Flight Specialist Agent with AWS serverless integration
        
        Args:
            config: System configuration dictionary
            security_module: Security guardrails instance
        """
        self.config = config
        self.security_module = security_module
        self.agent_config = config['agents']['flight_specialist']
        self.api_config = config['api_integration']['amadeus_gds']
        
        # Initialize Gemini model for conversational capabilities
        self.model = GenerativeModel("gemini-2.0-flash-exp")
        self.llm_config = config['llm_config']['parameters']
        
        # Session management for conversational flow
        self.active_sessions = {}
        
        logger.info("Flight Specialist Agent initialized")

    async def process_request(self, user_input: str, session_id: str) -> Any:
        """
        Main request processing with structured conversational flow
        
        Args:
            user_input: User query/request
            session_id: Unique session identifier
            
        Returns:
            AgentResponse: Structured response with flight data or guidance
        """
        logger.info(f"Flight Specialist processing request for session {session_id}")
        
        try:
            # Get or create session context
            session_context = self._get_session_context(session_id)
            
            # Determine current conversation stage
            conversation_stage = self._determine_conversation_stage(session_context)
            
            # Process based on conversation stage
            if conversation_stage == "greeting":
                response = await self._handle_greeting(user_input, session_id)
            elif conversation_stage == "requirements_collection":
                response = await self._collect_flight_requirements(user_input, session_id)
            elif conversation_stage == "flight_search":
                response = await self._execute_flight_search(session_id)
            elif conversation_stage == "flight_analysis":
                response = await self._analyze_flight_options(user_input, session_id)
            elif conversation_stage == "booking_process":
                response = await self._handle_booking_process(user_input, session_id)
            else:
                response = await self._handle_general_flight_query(user_input, session_id)
            
            # Update session context
            self._update_session_context(session_id, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Flight Specialist request processing failed: {e}")
            return self._create_error_response(str(e), session_id)

    def _get_session_context(self, session_id: str) -> Dict:
        """Retrieve or create session context for conversation continuity"""
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "stage": "greeting",
                "collected_data": {},
                "flight_preferences": {},
                "search_results": [],
                "conversation_history": [],
                "created_at": datetime.now()
            }
            logger.debug(f"Created new session context for {session_id}")
        
        return self.active_sessions[session_id]

    async def _handle_greeting(self, user_input: str, session_id: str) -> Dict:
        """
        Handle initial greeting and capability overview
        Structured conversational script flow as per specification
        """
        
        greeting_message = self.config['core_settings']['greeting_message']
        
        # Personalized greeting with capability explanation
        prompt = f"""
        As the Flight Specialist in the MAF system, provide a warm greeting and overview of capabilities.
        
        Base greeting: {greeting_message}
        
        User message: {user_input}
        
        Explain flight capabilities in layman terms:
        - Flight search across global routes
        - Real-time pricing and availability 
        - Flight booking and order creation
        - Airport and city code lookup
        - Price analysis and recommendations
        
        Ask what specific flight assistance they need and guide them through the process.
        Be friendly, professional, and proactive.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt, 
                generation_config=self.llm_config
            )
            
            return {
                "agent_id": "flight_specialist",
                "success": True,
                "data": {
                    "message": response.text,
                    "next_step": "requirements_collection",
                    "capabilities": [
                        "flight_search", "flight_pricing", "flight_booking", 
                        "airport_lookup", "price_analysis"
                    ]
                },
                "metadata": {"stage": "greeting_complete"},
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Greeting handling failed: {e}")
            return self._create_error_response(str(e), session_id)

    async def _collect_flight_requirements(self, user_input: str, session_id: str) -> Dict:
        """
        Collect flight requirements with technical translation to layman terms
        Ensures payload completeness for Amadeus GDS API calls
        """
        
        session_context = self.active_sessions[session_id]
        collected_data = session_context.get("collected_data", {})
        
        # Analyze user input to extract flight parameters
        extracted_params = await self._extract_flight_parameters(user_input)
        
        # Update collected data
        collected_data.update(extracted_params)
        session_context["collected_data"] = collected_data
        
        # Check completeness of required parameters
        required_fields = self.agent_config['guardrails']['parameter_validation']['required_fields']
        missing_fields = []
        
        for field in required_fields:
            # Map display names to API parameter names
            api_field = self._map_to_api_field(field)
            if api_field not in collected_data or not collected_data[api_field]:
                missing_fields.append(field)
        
        if missing_fields:
            # Request missing information in layman terms
            response = await self._request_missing_information(missing_fields, collected_data, session_id)
        else:
            # All required data collected, proceed to search
            response = await self._confirm_search_parameters(collected_data, session_id)
            session_context["stage"] = "flight_search"
        
        return response

    async def _extract_flight_parameters(self, user_input: str) -> Dict:
        """
        Extract flight parameters from natural language input
        Handles technical translation from layman terms to API parameters
        """
        
        prompt = f"""
        Extract flight search parameters from this user input: "{user_input}"
        
        Map to these API parameters:
        - originLocationCode (3-letter airport code)
        - destinationLocationCode (3-letter airport code) 
        - departureDate (YYYY-MM-DD format)
        - adults (number of adult passengers)
        - returnDate (YYYY-MM-DD format, optional)
        - children (number of child passengers, optional)
        - infant (number of infant passengers, optional)
        - travelClass (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
        
        Valid airport codes (from technical specifications): {self.config['test_data']['valid_airport_codes']}
        
        Return as JSON with extracted parameters, or empty dict if none found.
        Only use airport codes from the valid list above.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=self.llm_config
            )
            
            # Parse JSON response
            extracted_data = json.loads(response.text)
            
            # Validate extracted airport codes against security module
            if 'originLocationCode' in extracted_data:
                if not self.security_module.validate_airport_code(extracted_data['originLocationCode']):
                    del extracted_data['originLocationCode']
            
            if 'destinationLocationCode' in extracted_data:
                if not self.security_module.validate_airport_code(extracted_data['destinationLocationCode']):
                    del extracted_data['destinationLocationCode']
            
            logger.debug(f"Extracted flight parameters: {extracted_data}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            return {}

    async def _execute_flight_search(self, session_id: str) -> Dict:
        """
        Execute flight search via AWS serverless API Gateway → Lambda integration
        Rate limit: 500/s as per specification
        """
        
        session_context = self.active_sessions[session_id]
        search_params = session_context["collected_data"]
        
        # Construct API endpoint URL
        base_url = self.api_config['base_url']
        environment = self.api_config['environment'] 
        endpoint = "https://r9kpch95c6.execute-api.ap-southeast-2.amazonaws.com/test/flights/search"
        
        # Prepare query parameters
        query_params = {
            'adults': search_params.get('adults', 1),
            'originLocationCode': search_params.get('originLocationCode'),
            'destinationLocationCode': search_params.get('destinationLocationCode'),
            'departureDate': search_params.get('departureDate'),
        }
        
        # Add optional parameters if present
        if search_params.get('returnDate'):
            query_params['returnDate'] = search_params['returnDate']
        if search_params.get('children'):
            query_params['children'] = search_params['children']
        if search_params.get('infant'):
            query_params['infant'] = search_params['infant']
        if search_params.get('travelClass'):
            query_params['travelClass'] = search_params['travelClass']
        
        logger.info(f"Executing flight search with parameters: {query_params}")
        
        try:
            # Make API call to AWS serverless backend
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint, 
                    params=query_params,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        flight_data = await response.json()
                        
                        # Store search results in session context
                        self.active_sessions[session_id]["search_results"] = flight_data
                        self.active_sessions[session_id]["stage"] = "flight_analysis"
                        
                        # Translate technical response to user-friendly format
                        user_friendly_response = await self._translate_flight_results(flight_data)
                        
                        return {
                            "agent_id": "flight_specialist",
                            "success": True,
                            "data": {
                                "message": user_friendly_response,
                                "flight_offers": flight_data.get('data', {}).get('flightOffers', []),
                                "results_count": len(flight_data.get('data', {}).get('flightOffers', [])),
                                "next_step": "flight_analysis"
                            },
                            "metadata": {"stage": "search_complete", "api_response": "success"},
                            "timestamp": datetime.now()
                        }
                    else:
                        error_msg = f"API request failed with status {response.status}"
                        logger.error(error_msg)
                        return self._create_error_response(error_msg, session_id)
                        
        except asyncio.TimeoutError:
            error_msg = "Flight search request timed out"
            logger.error(error_msg)
            return self._create_error_response(error_msg, session_id)
        except Exception as e:
            error_msg = f"Flight search failed: {str(e)}"
            logger.error(error_msg)
            return self._create_error_response(error_msg, session_id)

    async def _translate_flight_results(self, flight_data: Dict) -> str:
        """
        Translate technical flight API response to user-friendly format
        Heavy lifting of technical translation to layman terms as per specification
        """
        
        flight_offers = flight_data.get('data', {}).get('flightOffers', [])
        
        if not flight_offers:
            return "No flights found for your search criteria. Please try different dates or destinations."
        
        # Prepare context for Gemini translation
        prompt = f"""
        Translate this flight search results into user-friendly format:
        
        Flight offers count: {len(flight_offers)}
        
        Sample flight data: {json.dumps(flight_offers[:2], indent=2)}
        
        Create a helpful summary that includes:
        1. Number of flight options found
        2. Price range overview
        3. Brief description of top 3 options with:
           - Airlines and flight numbers in simple terms
           - Departure and arrival times
           - Duration and stops
           - Price information
        4. Guidance on next steps (analysis, booking, modifications)
        
        Use friendly, professional language. Avoid technical jargon.
        Explain any airline codes, airport codes, or technical terms.
        """
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=self.llm_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Flight results translation failed: {e}")
            return f"Found {len(flight_offers)} flight options. Technical details are available for review."

    def _map_to_api_field(self, display_field: str) -> str:
        """Map user-friendly field names to API parameter names"""
        field_mapping = {
            'originLocationCode': 'originLocationCode',
            'destinationLocationCode': 'destinationLocationCode', 
            'departureDate': 'departureDate',
            'adults': 'adults',
            'returnDate': 'returnDate',
            'children': 'children',
            'infant': 'infant',
            'travelClass': 'travelClass'
        }
        
        return field_mapping.get(display_field, display_field)

    def _create_error_response(self, error_message: str, session_id: str) -> Dict:
        """Create standardized error response for A2A communication"""
        return {
            "agent_id": "flight_specialist",
            "success": False,
            "data": {},
            "metadata": {"error": error_message, "session_id": session_id},
            "timestamp": datetime.now(),
            "errors": [error_message]
        }

    # Additional methods for booking process, price analysis, etc.
    # ... (Implementation continues with remaining flight operations)
