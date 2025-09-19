from typing import Dict, Any, List
from base_agent import ADKAgent, Tool, Memory, A2AMessage, MessageType
import asyncio
from datetime import datetime, timedelta
import json

class AWSLambdaTool(Tool):
    """Base class for AWS Lambda integration tools"""
    def __init__(self, name: str, description: str, endpoint: str, api_key:
        str = None):
        super().__init__(name, description)
        self.endpoint = endpoint
        self.api_key = api_key or os.getenv('AWS_API_KEY')
        self.base_url = os.getenv('AWS_API_GATEWAY_URL')

    async def _call_lambda(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP call to AWS Lambda via API Gateway"""

        headers = {
            'Content-Type': 'application/json'
        }

        if self.api_key:
            headers['x-api-key'] = self.api_key
        url = f"{self.base_url}/{self.endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

class PriceAnalysisTool(Tool):
    """Tool for analyzing prices and providing insights"""
    def __init__(self):
        super().__init__(
            name="price_analysis",
            description="Analyze travel prices and provide insights"
        )

    async def execute(self, options: List[Dict[str, Any]], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze price options"""
        if not options:
            return {"status": "no_data", "message": "No options to analyze"}

        # Simple price analysis
        prices = [float(option.get("price", 0)) for option in options if "price" in option]

        if not prices:
            return {"status": "no_prices", "message": "No price data available"}
            analysis = {
                "status": "success",
                "price_range": {
                    "min": min(prices),
                    "max": max(prices),
                    "average": sum(prices) / len(prices)
                },
                "recommendations": []
            }

            # Add recommendations based on price analysis
            min_price_idx = prices.index(min(prices))
            analysis["recommendations"].append({
                "type": "best_value",
                "option_index": min_price_idx,
                "reason": "Lowest price option"
            })

            # Find middle-priced option

            sorted_prices = sorted(enumerate(prices), key=lambda x: x[1])
            mid_idx = sorted_prices[len(sorted_prices)//2][0]
            analysis["recommendations"].append({
                "type": "balanced",
                "option_index": mid_idx,
                "reason": "Good balance of price and options"
            })

            return analysis

class BookingCreationTool(AWSLambdaTool):
    """Tool for creating bookings via AWS Lambda"""
    def __init__(self):
        super().__init__(
            name="create_booking",
            description="Create travel bookings via AWS Lambda",
            endpoint="create-booking"
        )

    async def execute(self, booking_type: str, booking_details: Dict[str, Any], passenger_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute booking creation"""
        payload = {
            "booking_type": booking_type,
            "booking_details": booking_details,
            "passenger_info": passenger_info
        }

        try:
            result = await self._call_lambda(payload)
            return {
                "status": "success",
                "booking_reference": result.get("booking_reference"),
                "confirmation": result.get("confirmation"),
                "details": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "booking_details": payload
            }

class HotelSearchTool(AWSLambdaTool):
    """Tool for searching hotels via AWS Lambda"""
    def __init__(self):
        super().__init__(
        name="hotel_search",
        description="Search for hotels using Amadeus GDS via AWS Lambda",
        endpoint="hotel-search"
        )

    async def execute(self, city_code: str, check_in: str, check_out: str, guests: int = 1, rooms: int = 1, hotel_type: str = None) -> Dict[str, Any]:
        """Execute hotel search"""
        payload = {
            "city_code": city_code,
            "check_in": check_in,
            "check_out": check_out,
            "guests": guests,
            "rooms": rooms,
            "hotel_type": hotel_type
        }

        try:
            result = await self._call_lambda(payload)
            return {
                "status": "success",
                "hotels": result.get("hotels", []),
                "search_criteria": payload
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "search_criteria": payload
            }

class FlightSearchTool(AWSLambdaTool):
    """Tool for searching flights via AWS Lambda"""
    def __init__(self):
        super().__init__(
            name="flight_search",
            description="Search for flights using Amadeus GDS via AWS Lambda",
            endpoint="flight-search"
        )

    async def execute(self, origin: str, destination: str, departure_date:
    str, return_date: str = None, passengers: int = 1, cabin_class: str =
    "ECONOMY") -> Dict[str, Any]:
        """Execute flight search"""

        payload = {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "passengers": passengers,
            "cabin_class": cabin_class
        }

        try:
            result = await self._call_lambda(payload)
            return {
                "status": "success",
                "flights": result.get("flights", []),
                "search_criteria": payload
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "search_criteria": payload
            }

class TripPlanningTool(): 
    """Tool for planning multi-step trips"""
    def __init__(self):
        super().__init__(
            name="trip_planning",
            description="Plan complex multi-step travel itineraries"
        )

        async def execute(self, user_request: str, context: Dict[str, Any] = None)-> Dict[str, Any]:
            """Create a travel plan from user request"""
            # Simple intent extraction (in production, use more sophisticated NLP)
            request_lower = user_request.lower()

            plan = {
                "needs_flights": any(word in request_lower for word in ["flight", "fly", "plane", "travel to", "go to"]),
                "needs_hotels": any(word in request_lower for word in ["hotel", "stay", "accommodation", "room"]),
                "needs_context": True, # Always get context
                "trip_type": "leisure",
                "urgency": "normal"
            }

            # This is simplified - in production, use NER or similar
            if "to" in request_lower:
                parts = request_lower.split("to")
            if len(parts) > 1:
                destination = parts[-1].strip()
                plan["destination"] = destination

            # Extract dates
            if "tomorrow" in request_lower:
                plan["departure_date"] = (datetime.now() +
                timedelta(days=1)).isoformat()[:10]
            elif "next week" in request_lower:
                plan["departure_date"] = (datetime.now() +
                timedelta(days=7)).isoformat()[:10]

            # Determine trip purpose
            if any(word in request_lower for word in ["romantic", "honeymoon", "anniversary"]):
                plan["trip_type"] = "romantic"
            elif any(word in request_lower for word in ["business", "work", "meeting"]):
                plan["trip_type"] = "business"
            elif any(word in request_lower for word in ["family", "kids", "children"]):
                plan["trip_type"] = "family"
            return plan


class TripOrchestrator(ADKAgent):
    """Main orchestrator agent that coordinates other travel agents"""

    def __init__(self):
        tools = [TripPlanningTool(), PriceAnalysisTool()]
        super().__init__(
            name="trip-orchestrator",
            description="Coordinates travel planning across multiple specialized agents",
            tools=tools,
            memory=Memory(memory_type="conversation_buffer_window", k=15)
        )
        # Track ongoing tasks
        self.active_tasks = {}
        self.agent_responses = {}

        async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
            """Process user travel requests"""
            self.status = "processing"
            user_message = request.get("message", "")
            conversation_id = request.get("conversation_id", "default")

            # Store user message in memory
            self.memory.add_message("user", user_message)

            try:
                # Create travel plan
                plan_result = await self.use_tool("trip_planning",
                user_request=user_message)
                if plan_result.get("needs_flights") or plan_result.get("needs_hotels"):
                    # Coordinate with specialist agents
                    results = await self._coordinate_specialists(plan_result,
                    conversation_id)
                    response = await self._synthesize_response(results,
                    plan_result)
                else:
                    # Handle general travel questions
                    response = await self._handle_general_query(user_message)
                    self.memory.add_message("assistant", response.get("message", ""))
                    return response
            except Exception as e:
                error_response = {
                    "status": "error",
                    "message": f"I encountered an error while planning your trip: {str(e)}",
                    "suggestions": ["Please try rephrasing your request", "Makesure to include your destination"]
                }
                self.memory.add_message("assistant", error_response["message"])
                return error_response
            finally:
                self.status = "idle"

        async def _coordinate_specialists(self, plan: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
            """Coordinate with specialist agents using A2A protocol"""
            tasks = []
            # Create parallel tasks for different agents
            if plan.get("needs_flights"):
                flight_task = self._request_from_agent(
                    "flight-specialist",
                    "search_flights",
                    {
                        "origin": plan.get("origin", "NYC"), # Default for demo
                        "destination": plan.get("destination", "PAR"),
                        "departure_date": plan.get("departure_date"),
                        "trip_type": plan.get("trip_type")
                    },
                    conversation_id
                )
                tasks.append(("flights", flight_task))

            if plan.get("needs_hotels"):
                hotel_task = self._request_from_agent(
                    "hotel-specialist",
                    "search_hotels",
                    {
                        "destination": plan.get("destination", "PAR"),
                        "check_in": plan.get("departure_date"),
                        "trip_type": plan.get("trip_type")
                    },
                    conversation_id
                )
                tasks.append(("hotels", hotel_task))

            # Always get context
            context_task = self._request_from_agent("context-specialist", "get_travel_context",
                {
                    "destination": plan.get("destination", "PAR"),
                    "trip_type": plan.get("trip_type")
                },
                conversation_id
            )
            tasks.append(("context", context_task))

            # Wait for all tasks to complete with timeout
            results = {}
            try:
                completed_tasks = await asyncio.wait_for(
                    asyncio.gather(*[task[1] for task in tasks]),
                    timeout=30.0
                )
                for i, (task_name, _) in enumerate(tasks):
                    results[task_name] = completed_tasks[i]
            except asyncio.TimeoutError:
                results["error"] = "Some services are taking longer than expected"
            return results

        # In your TripOrchestrator class
        async def _request_from_agent(self, agent_name: str, action: str, params: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
            """Send A2A request to specialist agent and wait for response"""
            self.logger.debug(f"Sending A2A request to '{agent_name}' for action '{action}' with params: {params}")
            
            # Use the new method that handles the request-response pattern
            response = await self.send_request_and_wait(
                to_agent=agent_name,
                action=action,
                parameters=params,
                conversation_id=conversation_id,
                timeout=25.0
            )
            
            self.logger.debug(f"Received A2A response from {agent_name}: {response.get('status', 'unknown')}")
            return response

            
        async def _wait_for_response(self, message_id: str, timeout: float) -> Dict[str, Any]:
            """Wait for A2A response"""
            # This is simplified - in production, use proper async waiting mechanisms
            response_future = asyncio.Future()
            self.pending_requests[message_id] = response_future.set_result

            try:
                response = await asyncio.wait_for(response_future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                return {"status": "timeout", "message": "Agent did not respond intime"}


        async def _synthesize_response(self, results: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:    
            """Synthesize responses from multiple agents into coherent plan"""
            if "error" in results:
                return {
                    "status": "partial",
                    "message": "I found some information, but some services are running slowly. Here's what I have so far:",
                    "results": results
                }
            # Build response based on available results
            response_parts = []

            # Flight information
            if "flights" in results and results["flights"].get("status") == "success":
                flights = results["flights"].get("flights", [])
            if flights:
                response_parts.append(f"I found {len(flights)} flight options for your trip.")

            # Add price analysis
            if len(flights) > 1:
                price_analysis = await self.use_tool("price_analysis", options=flights, criteria=plan)

            if price_analysis.get("status") == "success":
                price_range = price_analysis["price_range"]
                response_parts.append(f"Prices range from ${price_range['min']:.0f} to ${price_range['max']:.0f}.")

            # Hotel information
            if "hotels" in results and results["hotels"].get("status") == "success":
                hotels = results["hotels"].get("hotels", [])
            if hotels:
                response_parts.append(f"I also found {len(hotels)} hotel options in your destination.")

            # Context information
            if "context" in results:
                context = results["context"]
            if context.get("weather"):
                response_parts.append(f"Weather tip: {context['weather']}")
            if context.get("local_tips"):
                response_parts.append(f"Local insight: {context['local_tips']}")
            if not response_parts:
                return {
                    "status": "no_results",
                    "message": "I'm having trouble finding options right now. Please try again in a moment.",
                    "suggestions": ["Check your destination spelling", "Try different dates"]
                }
            return {
                "status": "success",
                "message": " ".join(response_parts),
                "results": results,
                "next_actions": ["Would you like me to show you the flightoptions?", "Should I look for more hotel choices?"]
            }

        async def _handle_general_query(self, message: str) -> Dict[str, Any]:
            """Handle general travel questions"""
            return {
                "status": "info",
                "message": "I'm here to help you plan your travels! I can search for flights, hotels, and provide travel insights. What would you like to explore?",
                "suggestions": [
                "Search for flights to a destination",
                "Find hotels in a city",
                "Plan a complete trip" ]
            }

        async def process_a2a_request(self, message: A2AMessage) -> Dict[str, Any]:
            """Handle A2A requests from other agents"""
            # The orchestrator typically doesn't receive requests from other agents
            # but could handle coordination requests
            return {"status": "not_implemented"}

# from typing import Dict, Any, List
# from agents.base_agent import ADKAgent, Tool, Memory, A2AMessage, MessageType
# from tools.aws_tools import FlightSearchTool, HotelSearchTool, BookingCreationTool, PriceAnalysisTool
# import asyncio
# from datetime import datetime, timedelta
# import json
# import logging

# # BEST PRACTICE: Configure logging for visibility
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


# # FIX: Inherit from 'Tool', not 'tool'
# class TripPlanningTool(Tool):
#     """Tool for planning multi-step trips"""

#     def __init__(self):
#         # FIX: Correct indentation
#         super().__init__(
#             name="trip_planning",
#             description="Plan complex multi-step travel itineraries"
#         )

#     # FIX: Added missing colon at the end of the line
#     async def execute(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
#         """Create a travel plan from user request"""
#         request_lower = user_request.lower()

#         plan = {
#             "needs_flights": any(word in request_lower for word in ["flight", "fly", "plane", "travel to", "go to"]),
#             "needs_hotels": any(word in request_lower for word in ["hotel", "stay", "accommodation", "room"]),
#             "needs_context": True,
#             "trip_type": "leisure",
#             "urgency": "normal",
#             "destination": None
#         }

#         # REFACTOR: Safer way to extract destination
#         if "to" in request_lower:
#             parts = request_lower.split("to")
#             if len(parts) > 1:
#                 plan["destination"] = parts[-1].strip().split()[0].capitalize() # Try to get just the city name

#         if "tomorrow" in request_lower:
#             plan["departure_date"] = (datetime.now() + timedelta(days=1)).isoformat()[:10]
#         elif "next week" in request_lower:
#             plan["departure_date"] = (datetime.now() + timedelta(days=7)).isoformat()[:10]

#         if any(word in request_lower for word in ["romantic", "honeymoon", "anniversary"]):
#             plan["trip_type"] = "romantic"
#         elif any(word in request_lower for word in ["business", "work", "meeting"]):
#             plan["trip_type"] = "business"
#         elif any(word in request_lower for word in ["family", "kids", "children"]):
#             plan["trip_type"] = "family"
            
#         return plan


# # FIX: Inherit from 'ADKAgent', not 'ADKAgenet'
# class TripOrchestrator(ADKAgent):
#     """Main orchestrator agent that coordinates other travel agents"""

#     def __init__(self):
#         # FIX: Correct indentation
#         tools = [TripPlanningTool(), PriceAnalysisTool()]
#         super().__init__(
#             name="trip-orchestrator",
#             description="Coordinates travel planning across multiple specialized agents",
#             tools=tools,
#             memory=Memory(memory_type="conversation_buffer", k=15) # Assuming 'conversation_buffer' from base_agent
#         )
#         self.active_tasks = {}

#     async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
#         """Process user travel requests"""
#         self.status = "processing"
#         user_message = request.get("message", "")
#         conversation_id = request.get("conversation_id", "default")
#         self.memory.add_message("user", user_message)

#         try:
#             plan_result = await self.use_tool("trip_planning", user_request=user_message)
            
#             if not plan_result.get("destination"):
#                  return {"status": "clarification", "message": "I can help with that! Where would you like to go?"}

#             if plan_result.get("needs_flights") or plan_result.get("needs_hotels"):
#                 results = await self._coordinate_specialists(plan_result, conversation_id)
#                 response = await self._synthesize_response(results, plan_result)
#             else:
#                 response = await self._handle_general_query(user_message)
            
#             self.memory.add_message("assistant", response.get("message", ""))
#             return response
#         except Exception as e:
#             logger.error(f"Orchestration failed: {e}", exc_info=True)
#             error_response = {
#                 "status": "error",
#                 "message": f"I encountered an error while planning your trip: {str(e)}",
#                 "suggestions": ["Please try rephrasing your request", "Make sure to include your destination"]
#             }
#             self.memory.add_message("assistant", error_response["message"])
#             return error_response
#         finally:
#             self.status = "idle"

#     async def _coordinate_specialists(self, plan: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
#         """Coordinate with specialist agents using A2A protocol"""
#         tasks = []
#         destination = plan.get("destination")

#         if plan.get("needs_flights"):
#             tasks.append(self._request_from_agent(
#                 "flight-specialist", "search_flights",
#                 {"destination": destination, "departure_date": plan.get("departure_date")},
#                 conversation_id
#             ))
#         if plan.get("needs_hotels"):
#             tasks.append(self._request_from_agent(
#                 "hotel-specialist", "search_hotels",
#                 {"destination": destination, "check_in": plan.get("departure_date")},
#                 conversation_id
#             ))
#         tasks.append(self._request_from_agent(
#             "context-specialist", "get_travel_context",
#             {"destination": destination, "trip_type": plan.get("trip_type")},
#             conversation_id
#         ))

#         task_names = ["flights", "hotels", "context"] # Assuming this order
#         results = {}
#         try:
#             completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
#             for i, result in enumerate(completed_tasks):
#                  # This logic needs to be smarter if tasks are conditional
#                  if i < len(task_names):
#                     results[task_names[i]] = result
#         except Exception as e:
#             results["error"] = f"Coordination failed: {str(e)}"
#         return results

#     async def _request_from_agent(self, agent_name: str, action: str, params: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
#         """Send A2A request and await response."""
#         # REFACTOR: Simplified A2A logic. A production system needs a real message bus listener.
#         # The previous `_wait_for_response` with `asyncio.Future` would always time out
#         # because nothing was set up to ever call `set_result`.
#         logger.info(f"Sending A2A request to '{agent_name}' for action '{action}'")
#         try:
#             response = await self.send_a2a_message(
#                 to_agent=agent_name,
#                 message_type=MessageType.REQUEST,
#                 payload={"action": action, "parameters": params},
#                 conversation_id=conversation_id
#             )
#             # This is a placeholder for a real response mechanism.
#             # In a real system, you'd await a response correlated by message ID.
#             # For now, we assume the base_agent's send_a2a_message is adapted to be request-response.
#             # If not, this part needs a full implementation with a message bus.
#             return {"status": "simulated_success", "data": f"Data from {agent_name}"}
#         except Exception as e:
#             logger.error(f"Failed to get response from {agent_name}: {e}")
#             return {"status": "error", "message": f"Could not communicate with {agent_name}."}

#     async def _synthesize_response(self, results: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
#         """Synthesize responses from multiple agents into a coherent plan"""
#         response_parts = []
        
#         # Flight information
#         flights = results.get("flights", {}).get("flights", [])
#         if flights:
#             response_parts.append(f"I found {len(flights)} flight options.")
#             # Price analysis
#             if len(flights) > 1:
#                 price_analysis = await self.use_tool("price_analysis", options=flights, criteria=plan)
#                 if price_analysis.get("status") == "success":
#                     price_range = price_analysis["price_range"]
#                     response_parts.append(f"Prices range from ${price_range['min']:.0f} to ${price_range['max']:.0f}.")

#         # Hotel information
#         hotels = results.get("hotels", {}).get("hotels", [])
#         if hotels:
#             response_parts.append(f"I also found {len(hotels)} hotel options.")

#         # Context information
#         context = results.get("context", {})
#         # FIX: Look for 'cultural_tips' which is what context_specialist provides
#         cultural_tips = context.get("cultural_tips", {})
#         if cultural_tips:
#             greeting = cultural_tips.get('greeting', 'be respectful')
#             response_parts.append(f"A local tip: {greeting}.")

#         if not response_parts:
#             return {"status": "no_results", "message": "I'm having trouble finding options right now."}

#         return {
#             "status": "success",
#             "message": " ".join(response_parts),
#             "results": results,
#             "next_actions": ["Would you like me to show you the flight options?", "Should I look for more hotel choices?"]
#         }

#     async def _handle_general_query(self, message: str) -> Dict[str, Any]:
#         """Handle general travel questions"""
#         return {
#             "status": "info",
#             "message": "I can help you plan your travels! What would you like to explore?",
#             "suggestions": ["Search for flights to Paris", "Find hotels in Tokyo"]
#         }

#     async def process_a2a_request(self, message: A2AMessage) -> Dict[str, Any]:
#         """Handle A2A requests from other agents"""
#         logger.warning(f"Orchestrator received an unexpected A2A request from {message.from_agent}")
#         return {"status": "not_implemented", "message": "This agent orchestrates; it does not typically fulfill requests."}
