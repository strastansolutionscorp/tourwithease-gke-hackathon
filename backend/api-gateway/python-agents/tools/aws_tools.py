# tools/aws_tools.py
import httpx
import asyncio
import os
from typing import Dict, Any, Optional
from agents.base_agent import Tool


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
        if not self.base_url:
            logger.error("AWS_API_GATEWAY_URL environment variable is not set.")
            raise ValueError("AWS_API_GATEWAY_URL environment variable is not set.")

        headers = {
            'Content-Type': 'application/json'
        }

        if self.api_key:
            headers['x-api-key'] = self.api_key

        url = f"{self.base_url}/{self.endpoint}"

         # --- 3. ADDED LOGGING: Log the request before it is sent ---
        logger.info(f"Firing API request to Lambda...")
        logger.debug(f"URL: POST {url}")
        logger.debug(f"Payload: {payload}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)

        # --- 4. ADDED LOGGING: Log the response after it is received ---
        logger.info(f"Received API response with status code: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")

        response.raise_for_status()
        return response.json()



# class FlightSearchTool(AWSLambdaTool):
#     """Tool for searching flights via AWS Lambda"""
#     def __init__(self):
#         super().__init__(
#             name="flight_search",
#             description="Search for flights using Amadeus GDS via AWS Lambda",
#             endpoint="search"
#         )

#     async def execute(self, origin: str, destination: str, departure_date:
#     str, return_date: str = None, passengers: int = 1, cabin_class: str =
#     "ECONOMY") -> Dict[str, Any]:
#         """Execute flight search"""

#         payload = {
#             "origin": origin,
#             "destination": destination,
#             "departure_date": departure_date,
#             "return_date": return_date,
#             "passengers": passengers,
#             "cabin_class": cabin_class
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
 async def execute(self, origin: str, destination: str, departure_date: str, return_date: str = None, adults: int, children: int, infants: int, cabin_class: str, currency_code: str) -> Dict[str, Any]:
        """Execute flight search"""
        # FIX: Payload keys and values are now aligned with your backend API
        payload = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "returnDate": return_date,
            "adults": str(adults),
            "children": str(children),
            "infants": str(infants),
            "max": "100",
            "currencyCode": currency_code,
            "travelClass": cabin_class
        }
        try:
            result = await self._call_lambda(payload)
            logger.info(f"API response: {result}")
            return {
                "status": "success",
                "flights": result.get("data", []), # Assuming flights are under a 'data' key
                "search_criteria": payload
            }
        except Exception as e:
            logger.error(f"FlightSearchTool failed: {e}", exc_info=True)
            return {"status": "error", "message": str(e), "search_criteria": payload}



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