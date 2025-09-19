import asyncio
import os
import logging
from typing import Dict, Any, Optional, List
# Assuming base_agent.py contains the definitions for ADKAgent, Memory, A2AMessage, Tool
from base_agent import ADKAgent, Memory, A2AMessage, Tool
from dotenv import load_dotenv

class AWSLambdaTool(Tool):
    """Base class for AWS Lambda integration tools"""
    def __init__(self, name: str, description: str, endpoint: str, api_key: str = None):
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

class HotelSpecialist(ADKAgent):
    """Specialized agent for hotel-related operations"""
    def __init__(self):
        tools = [HotelSearchTool(), PriceAnalysisTool()]
        super().__init__(
            name="hotel-specialist",
            description="Expert in hotel searches, bookings, and accommodation recommendations",
            tools=tools,
            memory=Memory(memory_type="conversation_buffer", k=10)
        )
        async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
            """Process direct hotel requests"""
            action = request.get("action", "search")
            params = request.get("parameters", {})
            if action == "search_hotels":
                return await self._search_hotels(params)
            elif action == "analyze_hotels":
                return await self._analyze_hotels(params)
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
            if action == "search_hotels":
                return await self._search_hotels(parameters)
            elif action == "analyze_hotels":
                return await self._analyze_hotels(parameters)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown action: {action}",
                    "supported_actions": ["search_hotels", "analyze_hotels"]
                }

        async def _search_hotels(self, params: Dict[str, Any]) -> Dict[str, Any]:
            """Search for hotels using AWS Lambda"""
            try:
                # Extract parameters
                destination = params.get("destination", "PAR")
                check_in = params.get("check_in")
                check_out = params.get("check_out")
                guests = params.get("guests", 1)
                rooms = params.get("rooms", 1)
                trip_type = params.get("trip_type", "leisure")

                # Calculate check_out if not provided (default 3 nights)
                if check_in and not check_out:
                    from datetime import datetime, timedelta
                    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
                    check_out_date = check_in_date + timedelta(days=3)
                    check_out = check_out_date.strftime("%Y-%m-%d")
            
                # Determine hotel type based on trip type
                hotel_type = None
                if trip_type == "romantic":
                    hotel_type = "luxury"
                elif trip_type == "business":
                    hotel_type = "business"
                elif trip_type == "family":
                    hotel_type = "family"

                # Use hotel search tool
                search_result = await self.use_tool(
                    "hotel_search",
                    city_code=destination,
                    check_in=check_in,
                    check_out=check_out,
                    guests=guests,
                    rooms=rooms,
                    hotel_type=hotel_type
                )

                if search_result["status"] == "success":
                    hotels = search_result["hotels"]
                
                # Enhance results based on trip type
                if trip_type == "romantic":
                    hotels = self._prioritize_romantic_hotels(hotels)
                elif trip_type == "business":
                    hotels = self._prioritize_business_hotels(hotels)
                elif trip_type == "family":
                    hotels = self._prioritize_family_hotels(hotels)
                
                    # Add recommendations
                    search_result["recommendations"] = self._generate_hotel_recommendations(hotels, trip_type)
                    
                    # Store search in memory
                    self.memory.add_message("system", f"Searched hotels in {destination} for {check_in} to {check_out}, found {len(hotels)} options")
                    return search_result
                else:
                    return search_result

            except Exception as e:
                self.logger.error(f"Hotel search error: {e}")
                return {
                    "status": "error",
                    "message": f"Hotel search failed: {str(e)}",
                    "parameters": params
                }

    def _prioritize_romantic_hotels(self, hotels: list) -> list:
        """Prioritize hotels for romantic trips"""
        for hotel in hotels:
            score = 0
            # Prefer luxury hotels
            if hotel.get("category", 0) >= 4:
                score += 2
                # Prefer hotels with spa/wellness
                amenities = hotel.get("amenities", [])

            if any("spa" in amenity.lower() or "wellness" in amenity.lower() for amenity in amenities):
                score += 2
                # Prefer central locations
                if "city center" in hotel.get("location", "").lower():
                    score += 1

                # Prefer boutique/luxury chains
                if hotel.get("brand") in ["Four Seasons", "Ritz-Carlton", "St.Regis", "Le Labo"]:
                    score += 1
                    hotel["romantic_score"] = score
                    return sorted(hotels, key=lambda x: (-x.get("romantic_score", 0), float(x.get("price", 999999))))


    def _prioritize_business_hotels(self, hotels: list) -> list:
        """Prioritize hotels for business travel"""
        for hotel in hotels:
            score = 0
            # Prefer business amenities
            amenities = hotel.get("amenities", [])
            if any("business" in amenity.lower() or "conference" in amenity.lower() for amenity in amenities):
                score += 2

            # Prefer WiFi and workspaces
            if any("wifi" in amenity.lower() or "internet" in amenity.lower() for amenity in amenities):
                score += 1

            # Prefer airport proximity
            if "airport" in hotel.get("location", "").lower():
                score += 1

            # Prefer business hotel chains
            if hotel.get("brand") in ["Hilton", "Marriott", "Hyatt", "InterContinental"]:
                score += 1
                hotel["business_score"] = score

            return sorted(hotels, key=lambda x: (-x.get("business_score", 0), float(x.get("price", 999999))))

    def _prioritize_family_hotels(self, hotels: list) -> list:
        """Prioritize hotels for family travel"""
        for hotel in hotels:
            score = 0

            # Prefer family amenities
            amenities = hotel.get("amenities", [])
            if any("pool" in amenity.lower() or "kids" in amenity.lower() for amenity in amenities):
                score += 2

            # Prefer connecting rooms
            if any("family" in amenity.lower() or "connecting" in amenity.lower() for amenity in amenities):
                score += 1

            # Prefer safe neighborhoods
            if "family-friendly" in hotel.get("description", "").lower():
                score += 1
                hotel["family_score"] = score
                return  sorted(hotels, key=lambda x: (-x.get("family_score", 0), float(x.get("price", 999999))))

    def _generate_hotel_recommendations(self, hotels: list, trip_type: str) -> list:
        """Generate recommendations based on hotel analysis"""
        if not hotels:
            return []
            recommendations = []
            # Best value recommendation
            if len(hotels) > 0:
                recommendations.append({
                    "type": "best_value",
                    "hotel_index": 0,
                    "title": f"Perfect for your {trip_type} trip",
                    "reason": f"This hotel offers the best combination of amenities and location for {trip_type} travelers."
                })

            # Budget option
            if len(hotels) > 1:
                cheapest_idx = min(range(len(hotels)), key=lambda i:
                float(hotels[i].get("price", 999999)))
                recommendations.append({
                    "type": "budget_friendly",
                    "hotel_index": cheapest_idx,
                    "title": "Budget-friendly option",
                    "reason": "Great value for money while still meeting your needs."
                })

            # Luxury option
            if len(hotels) > 2:
                luxury_idx = max(range(len(hotels)), key=lambda i:
                hotels[i].get("category", 0))
                recommendations.append({
                    "type": "luxury",
                    "hotel_index": luxury_idx,
                    "title": "Premium experience",
                    "reason": "For the ultimate comfort and luxury during your stay."
            })

        return recommendations

    async def _analyze_hotels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze hotel options"""
        hotels = params.get("hotels", [])
        criteria = params.get("criteria", {})
        return await self.use_tool("price_analysis", options=hotels, criteria=criteria)


