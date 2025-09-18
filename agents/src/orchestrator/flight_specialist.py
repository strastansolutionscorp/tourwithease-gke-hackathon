# agents/flight_specialist.py
from agents.base_agent import ADKAgent, Memory, A2AMessage
from tools.aws_tools import FlightSearchTool, PriceAnalysisTool
from typing import Dict, Any


class FlightSpecialist(ADKAgent):
    """Specialized agent for flight-related operations"""
    def __init__(self):
        tools = [ FlightSearchTool(), PriceAnalysisTool() ]
        super().__init__(
            name="flight-specialist",
            description="Expert in flight searches, bookings, and price
            analysis",
            tools=tools,
            memory=Memory(memory_type="conversation_buffer", k=10)
        )
    async def process_request(self, request: Dict[str, Any]) -> Dict[str,Any]:
        """Process direct flight requests"""
        action = request.get("action", "search")
        params = request.get("parameters", {})
        if action == "search_flights":
            return await self._search_flights(params)
        elif action == "analyze_prices":
            return await self._analyze_prices(params)
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
        if action == "search_flights":
            result = await self._search_flights(parameters)
            return result
        elif action == "analyze_prices":
            result = await self._analyze_prices(parameters)
            return result
        else:
            return {
            "status": "error",
            "message": f"Unknown action: {action}",
            "supported_actions": ["search_flights", "analyze_prices"]
            }

    async def _search_flights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for flights using AWS Lambda"""
        try:
            # Extract parameters
            origin = params.get("origin", "NYC")
            destination = params.get("destination", "PAR")
            departure_date = params.get("departure_date")
            return_date = params.get("return_date")
            passengers = params.get("passengers", 1)
            cabin_class = params.get("cabin_class", "ECONOMY")
            trip_type = params.get("trip_type", "leisure")

            # Use flight search tool
            search_result = await self.use_tool(
                "flight_search",
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                passengers=passengers,
                cabin_class=cabin_class
            )
        if search_result["status"] == "success":
            flights = search_result["flights"]
            # Enhance results based on trip type
            if trip_type == "romantic":
                # Prefer evening flights, premium airlines
                flights = self._prioritize_romantic_flights(flights)
            elif trip_type == "business":
                # Prefer convenient times, premium airlines
                flights = self._prioritize_business_flights(flights)

            # Add price analysis
            if len(flights) > 1:
                price_analysis = await self.use_tool("price_analysis",
                options=flights, criteria=params)
                search_result["price_analysis"] = price_analysis
                # Store search in memory
            self.memory.add_message("system", f"Searched flights {origin} to {destination} on{departure_date}, found {len(flights)} options" )
                return search_result
            else:
                return search_result

        except Exception as e:
            self.logger.error(f"Flight search error: {e}")
            return {
                "status": "error",
                "message": f"Flight search failed: {str(e)}",
                "parameters": params
            }

    def _prioritize_romantic_flights(self, flights: list) -> list:
        """Prioritize flights suitable for romantic trips"""
        # Simple scoring - in production, use more sophisticated logic
        for flight in flights:
        score = 0
        # Prefer evening departures
        if "departure_time" in flight:
            hour = int(flight["departure_time"].split(":")[0])
        if 18 <= hour <= 21: # 6 PM to 9 PM
            score += 2

        # Prefer premium airlines
        if flight.get("airline") in ["Air France", "British Airways", "Lufthansa"]:
            score += 1

        # Prefer non-stop flights
        if flight.get("stops", 0) == 0:
            score += 1
            flight["romantic_score"] = score


        # Sort by romantic score (highest first) then by price
        return sorted(flights, key=lambda x: (-x.get("romantic_score", 0), float(x.get("price", 999999))))

        def _prioritize_business_flights(self, flights: list) -> list:
            """Prioritize flights suitable for business travel"""
            for flight in flights:
                score = 0
                # Prefer morning departures
                if "departure_time" in flight:
                    hour = int(flight["departure_time"].split(":")[0])
                if 6 <= hour <= 10: # 6 AM to 10 AM
                    score += 2

                # Prefer business airlines
                if flight.get("airline") in ["American Airlines", "Delta", "United"]:
                    score += 1

                # Prefer non-stop flights
                if flight.get("stops", 0) == 0:
                    score += 2
                flight["business_score"] = score

        return sorted(flights, key=lambda x: (-x.get("business_score", 0), Hotel Specialist Agent float(x.get("price", 999999))))

        async def _analyze_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze flight prices"""
            
            flights = params.get("flights", [])
            criteria = params.get("criteria", {})
            return await self.use_tool("price_analysis", options=flights, criteria=criteria)
