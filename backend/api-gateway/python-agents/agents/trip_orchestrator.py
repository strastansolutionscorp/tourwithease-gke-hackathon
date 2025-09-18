from typing import Dict, Any, List
from agents.base_agent import ADKAgent, Tool, Memory, A2AMessage, MessageType
from tools.aws_tools import FlightSearchTool, HotelSearchTool,
BookingCreationTool, PriceAnalysisTool
import asyncio
from datetime import datetime, timedelta
import json


class TripPlanningTool(tool): 
    
    """Tool for planning multi-step trips"""

    def __init__(self):
        super().__init__(
        name="trip_planning",
        description="Plan complex multi-step travel itineraries"
    )

    async def execute(self, user_request: str, context: Dict[str, Any] = None)
    -> Dict[str, Any]:
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


class TripOrchestrator(ADKAgenet):
    """Main orchestrator agent that coordinates other travel agents"""

    def __init__(self):
    tools = [TripPlanningTool(), PriceAnalysisTool()]
    super().__init__(
        name="trip-orchestrator",
        description="Coordinates travel planning across multiple
        specialized agents",
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
            "message": f"I encountered an error while planning your trip:
            {str(e)}",
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

    async def _request_from_agent(self, agent_name: str, action: str, params: Dict[str, Any], conversation_id: str) -> Dict[str, Any]:
        """Send A2A request to specialist agent"""
        request_payload = {
            "action": action,
            "parameters": params
        }

        # Send A2A message
        message_id = await self.send_a2a_message(
            to_agent=agent_name,
            message_type=MessageType.REQUEST,
            payload=request_payload,
            conversation_id=conversation_id
        )

        # Wait for response (simplified - in production, use proper async patterns)
        response = await self._wait_for_response(message_id, timeout=25.0)
        return response
        
    async def _wait_for_response(self, message_id: str, timeout: float) -> Dict[str, Any]:
        """Wait for A2A response"""
        # This is simplified - in production, use proper async waiting mechanisms
        response_future = asyncio.Future()
        self.pending_requests[message_id] = response_future.set_result

        try:
            response = await asyncio.wait_for(response_future,
            timeout=timeout)
        return response
            except asyncio.TimeoutError:
        return {"status": "timeout", "message": "Agent did not respond intime"}


    async def _synthesize_response(self, results: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:    
        """Synthesize responses from multiple agents into coherent plan"""
        if "error" in results:
        return {
            "status": "partial",
            "message": "I found some information, but some services are
            running slowly. Here's what I have so far:",
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
            price_analysis = await self.use_tool("price_analysis",
            options=flights, criteria=plan)

        if price_analysis.get("status") == "success":
            price_range = price_analysis["price_range"]
            response_parts.append(f"Prices range from
            ${price_range['min']:.0f} to ${price_range['max']:.0f}.")

        # Hotel information
        if "hotels" in results and results["hotels"].get("status") == "success":
            hotels = results["hotels"].get("hotels", [])
        if hotels:
            response_parts.append(f"I also found {len(hotels)} hotel
            options in your destination.")

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