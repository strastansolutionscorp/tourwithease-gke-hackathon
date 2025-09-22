#v2
# agents/aws_tools/tool.py (Updated)
import httpx
import asyncio
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Assuming base_agent is in parent directory
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from base_agent import Tool

logger = logging.getLogger(__name__)

class AWSLambdaTool(Tool):
    """Enhanced base class for AWS Lambda integration with ADK support"""
    
    def __init__(self, name: str, description: str, endpoint: str, api_key: str = None):
        super().__init__(name, description)
        self.endpoint = endpoint
        self.api_key = api_key or os.getenv('AWS_API_KEY', 'ziU53MRcWq2FQTSDaF1sf5lK2hm9xZmR3HPYUBBD')
        self.base_url = os.getenv('AWS_API_GATEWAY_URL', 
                                'https://ta2z6r502h.execute-api.ap-southeast-1.amazonaws.com/dev')
        self.logger = logging.getLogger(f"aws_tool_{name}")

    async def _call_lambda(self, payload: Dict[str, Any], method: str = "GET") -> Dict[str, Any]:
        """Make HTTP call to AWS Lambda via API Gateway with ADK event tracking"""
        
        if not self.base_url:
            raise ValueError("AWS_API_GATEWAY_URL environment variable is not set.")

        headers = { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if self.api_key:
            headers['x-api-key'] = self.api_key

        url = f"{self.base_url}/{self.endpoint}"
        
        # ADK-style event logging
        self.logger.info(f"🚀 ADK EVENT: Starting AWS API call to {url}")
        
        start_time = datetime.now()

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                self.logger.info(f"📡 Making {method} request to AWS API Gateway")
                
                if method == "GET":
                    response = await client.get(url, params=payload, headers=headers)
                else:
                    response = await client.post(url, json=payload, headers=headers)

                response.raise_for_status()
                result = response.json()
                
                logger.info(result)
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                self.logger.info(f"✅ ADK EVENT: AWS API call successful in {duration}s")
                
                return {
                    "api_response": result,
                    # "flights": result["flights"],
                    "metadata": {
                        "endpoint": url,
                        "method": method,
                        "response_time": duration,
                        "status_code": response.status_code,
                        "timestamp": end_time.isoformat()
                    }
                }

            except httpx.HTTPStatusError as e:
                self.logger.error(f"❌ ADK EVENT: AWS API HTTP error {e.response.status_code}")
                raise
            except Exception as e:
                self.logger.error(f"❌ ADK EVENT: AWS API general error: {e}")
                raise
            
class HotelGeocodeSearchTool(AWSLambdaTool):
    """Tool for searching hotels via AWS Lambda"""
    def __init__(self):
        super().__init__(
            name="hotel_geocode_search",
            description="Search for hotels using Amadeus GDS via AWS Lambda",
            endpoint="hotels/geocode"
        )

    async def execute(self, 
                     cityCode: str, 
                     latitude: float,
                     longitude: float,
                     radius: int,
                     radiusUnit: str,
                     children: int,
                     adults: int,
                     chainCodes: str,
                     amenities: str,
                     ratings: str,
                     hotelSource: str,
                     checkIn: str, 
                     checkOut: str,
                     pageLimit: int,
                     pageOffset: int,
                     ) -> Dict[str, Any]:
        """Execute hotel search"""
        
        payload = {
            "cityCode": cityCode,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "radiusUnit": radiusUnit,
            "children": children,
            "adults": adults,
            "chainCodes": chainCodes,
            "amenities": amenities,
            "ratings": ratings,
            "hotelSource": hotelSource,
            "checkIn": checkIn, 
            "checkOut": checkOut,
            "pageLimit": pageLimit,
            "pageOffset": pageOffset,
        }

        try:
            result = await self._call_lambda(payload)
            logger.info(f"Result {result}")
            return {
                "status": "success",
                "result": result.get("result"),
                "search_criteria": payload
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "search_criteria": payload
            }
            
class HotelSearchTool(AWSLambdaTool):
    """Tool for searching hotels via AWS Lambda"""
    def __init__(self):
        super().__init__(
            name="hotel_search_tool",
            description="Search for hotels using Amadeus GDS via AWS Lambda",
            endpoint="hotels/search"
        )

    async def execute(self, 
                     hotelIds: str, 
                     adults: int,
                     checkInDate: str, 
                     checkOutDate: str,
                     ) -> Dict[str, Any]:
        """Execute hotel search"""
        
        payload = {
            "hotelIds": hotelIds,
            "adults": adults,
            "checkInDate": checkInDate, 
            "checkOutDate": checkOutDate,
        }

        try:
            result = await self._call_lambda(payload)
            logger.info(f"Result {result}")
            return {
                "status": "success",
                "result": result.get("result"),
                "search_criteria": payload
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "search_criteria": payload
            }
            
class HotelBookingTool(AWSLambdaTool):
    """Tool for booking hotels via AWS Lambda API Gateway using POST method"""
    
    def __init__(self):
        super().__init__(
            name="hotel_booking",
            description="Book hotel reservations using POST method to Amadeus GDS via AWS Lambda API Gateway",
            endpoint="booking/hotel-orders-v2"
        )

    async def execute(self, 
                     hotelOfferId: str,
                     primary_guest: Dict[str, Any],
                     additional_guests: List[Dict[str, Any]] = None,
                     payment_info: Dict[str, Any] = None,
                     travel_agent_email: str = None) -> Dict[str, Any]:
        """
        Execute hotel booking using POST method with guest information and payment details
        """
        
        self.logger.info(f"🎫 Initiating hotel booking POST request for offer: {hotelOfferId}")
        
        # Build complete booking payload
        booking_payload = {
            "data": {
                "type": "hotel-order",
                "guests": self._build_guest_list(primary_guest, additional_guests),
                "travelAgent": {
                    "contact": {
                        "email": travel_agent_email or primary_guest["email"]
                    }
                },
                "roomAssociations": [
                    {
                        "guestReferences": [{"guestReference": "1"}],
                        "hotelOfferId": hotelOfferId
                    }
                ],
                "payment": self._build_payment_info(payment_info, primary_guest)
            }
        }
        
        try:
            # ✅ CRITICAL: Use POST method for booking
            result = await self._call_lambda(booking_payload, method="POST")
            self.logger.info(f"Result: {result}")
            api_response = result["api_response"]
            self.logger.info(f"API Response: {result}")
            metadata = result["metadata"]
            
            self.logger.info("✅ Hotel booking POST request completed")
            
            # Process booking response
            if api_response.get("success") or api_response.get("data"):
                booking_data = api_response.get("data", api_response)
                
                return {
                    "status": "success",
                    "booking_confirmed": True,
                    "confirmation_number": booking_data.get("id", "BOOKING_CONFIRMED"),
                    "booking_reference": booking_data.get("bookingReference", "REF_" + hotelOfferId[:8]),
                    "hotel_offer_id": hotelOfferId,
                    "booking_details": {
                        "primary_guest": primary_guest,
                        "total_guests": len(booking_payload["data"]["guests"]),
                        "booking_type": "hotel-order",
                        "payment_method": "CREDIT_CARD"
                    },
                    "api_metadata": metadata,
                    "method_used": "POST",
                    "source": "AWS_API_Gateway_Booking"
                }
            else:
                error_message = api_response.get("error", {}).get("detail", "Unknown booking error")
                
                return {
                    "status": "booking_failed",
                    "booking_confirmed": False,
                    "error_message": error_message,
                    "hotel_offer_id": hotelOfferId,
                    "method_used": "POST",
                    "api_response": api_response
                }
            
        except Exception as e:
            self.logger.error(f"❌ Hotel booking POST request failed: {e}")
            return {
                "status": "error",
                "booking_confirmed": False,
                "message": str(e),
                "hotel_offer_id": hotelOfferId,
                "method_used": "POST"
            }

    def _build_guest_list(self, primary_guest: Dict[str, Any], additional_guests: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Build the guest list for booking"""
        guests = []
        
        # Primary guest (tid: 1)
        guests.append({
            "tid": 1,
            "title": primary_guest["title"].upper(),
            "firstName": primary_guest["firstName"].upper(),
            "lastName": primary_guest["lastName"].upper(),
            "phone": primary_guest.get("phone", "+1234567890"),
            "email": primary_guest["email"]
        })
        
        # Additional guests if provided
        if additional_guests:
            for i, guest in enumerate(additional_guests, start=2):
                guests.append({
                    "tid": i,
                    "title": guest.get("title", "MR").upper(),
                    "firstName": guest["firstName"].upper(),
                    "lastName": guest["lastName"].upper(),
                    "phone": guest.get("phone", primary_guest.get("phone", "+1234567890")),
                    "email": guest.get("email", primary_guest["email"])
                })
        
        return guests

    def _build_payment_info(self, payment_info: Dict[str, Any] = None, primary_guest: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build payment information for booking"""
        if not payment_info:
            # Default payment info for testing
            payment_info = {
                "vendorCode": "VI",
                "cardNumber": "4151289722471370", 
                "expiryDate": "2026-08",
                "holderName": f"{primary_guest['firstName']} {primary_guest['lastName']}"
            }
        
        return {
            "method": "CREDIT_CARD",
            "paymentCard": {
                "paymentCardInfo": {
                    "vendorCode": payment_info.get("vendorCode", "VI"),
                    "cardNumber": payment_info.get("cardNumber"),
                    "expiryDate": payment_info.get("expiryDate"),
                    "holderName": payment_info.get("holderName", f"{primary_guest['firstName']} {primary_guest['lastName']}").upper()
                }
            }
        }

class FlightSearchTool(AWSLambdaTool):
    """Enhanced flight search tool with ADK integration"""
    
    def __init__(self):
        super().__init__(
            name="flight_search",
            description="Search for flights using Amadeus GDS via AWS Lambda API Gateway",
            endpoint="flights/search"
        )

    async def execute(self, 
                     origin: str, 
                     destination: str, 
                     departure_date: str, 
                     return_date: str = None, 
                     adults: int = 1, 
                     children: int = 0, 
                     infants: int = 0, 
                     cabin_class: str = "ECONOMY",
                     currency_code: str = "USD") -> Dict[str, Any]:
        """Execute flight search with proper ADK event handling"""
        
        # Build payload for API Gateway
        payload = {
            "originLocationCode": origin.upper(),
            "destinationLocationCode": destination.upper(), 
            "departureDate": departure_date,
            "returnDate": return_date,
            "adults": str(adults),
            "max": "100",
            "currencyCode": currency_code,
            "travelClass": cabin_class.upper()
        }
        
        # Add optional parameters
        if return_date:
            payload["returnDate"] = return_date
        if children > 0:
            payload["children"] = str(children)
        if infants > 0:
            payload["infants"] = str(infants)

        try:
            # Call AWS API Gateway
            result = await self._call_lambda(payload, method="GET")

            api_response = result["api_response"]  # Get the raw API response
            metadata = result["metadata"]
            
            self.logger.info(f"✅ FlightSearchTool API call successful")
            
            # ✅ FIXED: Parse your actual API response structure
            flights = []
            
            if api_response and api_response.get("success"):
                # Extract from the 'data' array (your actual structure)
                if "data" in api_response and isinstance(api_response["data"], list):
                    flights = api_response["data"]
                    self.logger.info(f"✈️ Successfully extracted {len(flights)} flights from API response")
                else:
                    self.logger.warning(f"⚠️ No 'data' array found in API response")
            else:
                self.logger.error(f"❌ API response success=false or missing")
            
            return {
                "status": "success",
                "flights": flights,
                "search_criteria": payload,
                "total_results": len(flights),
                "api_metadata": metadata,
                "source": "AWS_API_Gateway_Amadeus"
            }
            # return {
            #     "status": "success",
            #     "flights": result.get("flights", []),
            #     "search_criteria": payload
            # }
            # api_response = result["api_response"]
            # metadata = result["metadata"]
            
            # # Extract flight data based on your API response structure
            # flight_offers = []
            # if api_response and "data" in api_response:
            #     flight_offers = api_response["data"].get("flightOffers", [])
            # elif api_response and "flightOffers" in api_response:
            #     flight_offers = api_response["flightOffers"]
            # elif api_response and isinstance(api_response, list):
            #     flight_offers = api_response
            
            # self.logger.info(f"✈️  Found {len(flight_offers)} flight offers")
            
            # return {
            #     "status": "success",
            #     "flights": flight_offers,
            #     "search_criteria": payload,
            #     "total_results": len(flight_offers),
            #     "api_metadata": metadata,
            #     "source": "AWS_API_Gateway_Amadeus"
            # }
            
        except Exception as e:
            self.logger.error(f"Flight search failed: {e}")
            return {
                "status": "error", 
                "message": str(e), 
                "search_criteria": payload,
                "flights": [],
                "source": "AWS_API_Gateway_Amadeus"
            }

#v1 not working to parsing
# class FlightPricingOffersTool(AWSLambdaTool):
#     """NEW: Flight pricing offers tool for detailed pricing analysis"""
    
#     def __init__(self):
#         super().__init__(
#             name="flight_pricing_offers",
#             description="Get detailed flight pricing offers with booking requirements via AWS Lambda API Gateway",
#             endpoint="flights/pricing"
#         )

#     async def execute(self, flight_offers: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """
#         Execute flight pricing offers request to get detailed pricing and booking requirements.
        
#         Args:
#             flight_offers: List of flight offers from flight search to get detailed pricing for
            
#         Returns:
#             Dict containing detailed pricing offers with booking requirements
#         """
        
#         # Build payload for flight pricing offers API
#         payload = {
#             "data": {
#                 "type": "flight-offers-pricing",
#                 "data": flight_offers
#             }
#         }
        
#         self.logger.info(f"💰 Requesting pricing for {len(flight_offers)} flight offers")

#         try:
#             # Call AWS API Gateway for flight pricing offers
#             result = await self._call_lambda(payload, method="POST")
#             api_response = result["api_response"]
#             metadata = result["metadata"]
            
#             self.logger.info(f"✅ Flight pricing offers API call successful")
            
#             # Parse the response structure you provided
#             if api_response and api_response.get("success") and "data" in api_response:
#                 pricing_data = api_response["data"]
                
#                 # Extract pricing offers
#                 pricing_offers = pricing_data.get("data", {}).get("flightOffers", [])
#                 booking_requirements = pricing_data.get("data", {}).get("bookingRequirements", {})
#                 dictionaries = pricing_data.get("dictionaries", {})
                
#                 # Analyze pricing information
#                 pricing_analysis = self._analyze_pricing_offers(pricing_offers)
                
#                 return {
#                     "status": "success",
#                     "pricing_offers": pricing_offers,
#                     "booking_requirements": booking_requirements,
#                     "dictionaries": dictionaries,
#                     "pricing_analysis": pricing_analysis,
#                     "total_offers": len(pricing_offers),
#                     "api_metadata": metadata,
#                     "source": "AWS_API_Gateway_PricingOffers"
#                 }
#             else:
#                 return {
#                     "status": "error",
#                     "message": "Invalid response format from pricing offers API",
#                     "raw_response": api_response,
#                     "source": "AWS_API_Gateway_PricingOffers"
#                 }
            
#         except Exception as e:
#             self.logger.error(f"Flight pricing offers failed: {e}")
#             return {
#                 "status": "error", 
#                 "message": str(e), 
#                 "request_payload": payload,
#                 "source": "AWS_API_Gateway_PricingOffers"
#             }
    
#     def _analyze_pricing_offers(self, pricing_offers: List[Dict[str, Any]]) -> Dict[str, Any]:
#         """Analyze pricing offers to extract key information"""
        
#         if not pricing_offers:
#             return {"error": "No pricing offers to analyze"}
        
#         analysis = {
#             "total_offers": len(pricing_offers),
#             "price_breakdown": [],
#             "traveler_summary": {},
#             "itinerary_summary": {},
#             "booking_features": []
#         }
        
#         for offer in pricing_offers:
#             # Extract price information
#             price_info = offer.get("price", {})
#             if price_info:
#                 price_breakdown = {
#                     "total_price": price_info.get("total", "0"),
#                     "base_price": price_info.get("base", "0"),
#                     "currency": price_info.get("currency", "USD"),
#                     "grand_total": price_info.get("grandTotal", "0"),
#                     "fees": price_info.get("fees", [])
#                 }
#                 analysis["price_breakdown"].append(price_breakdown)
            
#             # Extract traveler pricing
#             traveler_pricings = offer.get("travelerPricings", [])
#             for traveler in traveler_pricings:
#                 traveler_type = traveler.get("travelerType", "UNKNOWN")
#                 traveler_price = traveler.get("price", {}).get("total", "0")
                
#                 if traveler_type not in analysis["traveler_summary"]:
#                     analysis["traveler_summary"][traveler_type] = {
#                         "count": 0,
#                         "total_price": 0
#                     }
                
#                 analysis["traveler_summary"][traveler_type]["count"] += 1
#                 try:
#                     analysis["traveler_summary"][traveler_type]["total_price"] += float(traveler_price)
#                 except (ValueError, TypeError):
#                     pass
            
#             # Extract itinerary information
#             itineraries = offer.get("itineraries", [])
#             analysis["itinerary_summary"]["total_itineraries"] = len(itineraries)
            
#             total_segments = 0
#             co2_emissions = []
            
#             for itinerary in itineraries:
#                 segments = itinerary.get("segments", [])
#                 total_segments += len(segments)
                
#                 for segment in segments:
#                     emissions = segment.get("co2Emissions", [])
#                     for emission in emissions:
#                         co2_emissions.append({
#                             "weight": emission.get("weight", 0),
#                             "unit": emission.get("weightUnit", "KG"),
#                             "cabin": emission.get("cabin", "ECONOMY")
#                         })
            
#             analysis["itinerary_summary"]["total_segments"] = total_segments
#             analysis["itinerary_summary"]["co2_emissions"] = co2_emissions
            
#             # Extract booking features
#             if offer.get("instantTicketingRequired"):
#                 analysis["booking_features"].append("Instant ticketing required")
#             if offer.get("paymentCardRequired"):
#                 analysis["booking_features"].append("Payment card required")
#             if not offer.get("nonHomogeneous", True):
#                 analysis["booking_features"].append("Homogeneous pricing")
        
#         return analysis
class FlightPricingOffersTool(AWSLambdaTool):
    """FIXED: Flight pricing offers tool with proper API triggering"""
    
    def __init__(self):
        super().__init__(
            name="flight_pricing_offers",
            description="Get detailed flight pricing offers with booking requirements via AWS Lambda API Gateway",
            endpoint="flights/pricing"
        )

    async def execute(self, flight_offers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        FIXED: Execute flight pricing offers request with proper API call and response parsing.
        """
        
        # FIXED: Build payload exactly as your specification
        payload = {
            "data": {
                "type": "flight-offers-pricing",
                "flightOffers": flight_offers  # Use the correct key "flightOffers"
            }
        }
        
        self.logger.info(f"💰 Requesting detailed pricing for {len(flight_offers)} flight offers")
        self.logger.info("🔧 TRIGGERING POST request to AWS API Gateway /flights/pricing endpoint")

        try:
            # FIXED: Call AWS API Gateway for flight pricing offers with POST method
            result = await self._call_lambda(payload, method="POST")
            api_response = result["api_response"]
            metadata = result["metadata"]
            
            self.logger.info(f"✅ Flight pricing offers API call successful")
            self.logger.info(f"📊 API Gateway POST response received successfully")
            
            # ENHANCED: Parse your exact response structure
            if api_response and api_response.get("success") and "data" in api_response:
                
                # Extract nested data structure
                outer_data = api_response["data"]
                inner_data = outer_data.get("data", {})
                
                # Extract all components from your response structure
                pricing_offers = inner_data.get("flightOffers", [])
                booking_requirements = inner_data.get("bookingRequirements", {})
                dictionaries = outer_data.get("dictionaries", {})
                
                self.logger.info(f"📊 Parsed {len(pricing_offers)} pricing offers with booking requirements")
                
                # ENHANCED: Process each pricing offer for AI consumption
                processed_offers = []
                for offer in pricing_offers:
                    processed_offer = self._process_pricing_offer_for_ai(offer)
                    processed_offers.append(processed_offer)
                
                # ENHANCED: Process booking requirements for AI
                processed_booking_requirements = self._process_booking_requirements(booking_requirements)
                
                # ENHANCED: Process dictionaries for AI
                processed_dictionaries = self._process_dictionaries(dictionaries)
                
                # Comprehensive pricing analysis
                pricing_analysis = self._analyze_comprehensive_pricing(pricing_offers, booking_requirements)
                
                return {
                    "status": "success",
                    "pricing_offers": pricing_offers,  # AI-friendly processed offers
                    "raw_pricing_offers": pricing_offers,  # Keep original for reference
                    "booking_requirements": processed_booking_requirements,
                    "dictionaries": processed_dictionaries,
                    "pricing_analysis": pricing_analysis,
                    "total_offers": len(pricing_offers),
                    "api_metadata": metadata,
                    "source": "AWS_API_Gateway_PricingOffers_Enhanced",
                    "ai_processed": True
                }
            else:
                self.logger.error(f"❌ Invalid response format from pricing offers API")
                return {
                    "status": "error",
                    "message": "Invalid response format from pricing offers API",
                    "raw_response": api_response,
                    "source": "AWS_API_Gateway_PricingOffers"
                }
            
        except Exception as e:
            self.logger.error(f"❌ Flight pricing offers failed: {e}")
            self.logger.error(f"📊 POST request to {self.base_url}/{self.endpoint} failed")
            return {
                "status": "error", 
                "message": str(e), 
                "request_payload": payload,
                "source": "AWS_API_Gateway_PricingOffers"
            }
    
    # Keep all your existing helper methods (_process_pricing_offer_for_ai, etc.)


class PriceAnalysisTool(AWSLambdaTool):
    """Enhanced price analysis tool with price metrics API integration"""
    
    def __init__(self):
        super().__init__(
            name="price_analysis",
            description="Analyze flight prices using Amadeus price metrics API",
            endpoint="flights/price-analysis"  # Updated endpoint for price metrics
        )

    async def execute(self, 
                     origin: str,
                     destination: str, 
                     departure_date: str,
                     return_date: str = None,
                     currency_code: str = "USD",
                     **kwargs) -> Dict[str, Any]:
        """Execute price analysis using price metrics API"""
        
        # Build payload for price metrics API
        payload = {
            "originIataCode": origin.upper(),
            "destinationIataCode": destination.upper(),
            "departureDate": departure_date,
            "currencyCode": currency_code,
            "oneWay": return_date is None  # True for one-way, False for round-trip
        }
        
        # Add return date if provided
        if return_date:
            payload["returnDate"] = return_date

        try:
            # Call AWS API Gateway for price metrics
            result = await self._call_lambda(payload, method="GET")
            api_response = result["api_response"]
            metadata = result["metadata"]
            
            self.logger.info(f"📊 Price analysis API response received")
            
            # Parse the price metrics response format you provided
            if api_response and api_response.get("success") and "data" in api_response:
                price_data = api_response["data"]["data"]
                
                if price_data and len(price_data) > 0:
                    price_metrics = price_data[0].get("priceMetrics", [])
                    
                    # Extract price quartiles
                    price_quartiles = {}
                    for metric in price_metrics:
                        ranking = metric.get("quartileRanking", "").upper()
                        amount = float(metric.get("amount", 0))
                        price_quartiles[ranking] = amount
                    
                    # Generate comprehensive analysis
                    analysis = {
                        "status": "success",
                        "route_info": {
                            "origin": price_data[0].get("origin", {}).get("iataCode", origin),
                            "destination": price_data[0].get("destination", {}).get("iataCode", destination),
                            "departure_date": price_data[0].get("departureDate", departure_date),
                            "currency": price_data[0].get("currencyCode", currency_code),
                            "trip_type": "one-way" if price_data[0].get("oneWay") else "round-trip"
                        },
                        "price_quartiles": price_quartiles,
                        "price_statistics": {
                            "minimum_price": price_quartiles.get("MINIMUM", 0),
                            "first_quartile": price_quartiles.get("FIRST", 0),
                            "median_price": price_quartiles.get("MEDIUM", 0),
                            "third_quartile": price_quartiles.get("THIRD", 0),
                            "maximum_price": price_quartiles.get("MAXIMUM", 0)
                        },
                        "recommendations": []
                    }
                    
                    # Generate recommendations based on quartiles
                    min_price = price_quartiles.get("MINIMUM", 0)
                    median_price = price_quartiles.get("MEDIUM", 0)
                    max_price = price_quartiles.get("MAXIMUM", 0)
                    
                    if min_price > 0:
                        analysis["recommendations"].append({
                            "type": "budget_option",
                            "price_range": f"{min_price} - {price_quartiles.get('FIRST', min_price)}",
                            "description": f"Budget flights start from {min_price} {currency_code}",
                            "recommendation": "Best deals available in the minimum price range"
                        })
                    
                    if median_price > 0:
                        analysis["recommendations"].append({
                            "type": "balanced_option",
                            "price": median_price,
                            "description": f"Median price flights around {median_price} {currency_code}",
                            "recommendation": "Good balance of price and flight options"
                        })
                    
                    if max_price > min_price:
                        savings = max_price - min_price
                        analysis["recommendations"].append({
                            "type": "savings_opportunity",
                            "potential_savings": savings,
                            "description": f"Save up to {savings} {currency_code} by choosing budget options",
                            "recommendation": "Consider flexible dates for better deals"
                        })
                    
                    analysis["api_metadata"] = metadata
                    analysis["source"] = "AWS_API_Gateway_PriceMetrics"
                    
                    return analysis
                else:
                    return {
                        "status": "no_data",
                        "message": "No price metrics data available for this route",
                        "search_criteria": payload,
                        "source": "AWS_API_Gateway_PriceMetrics"
                    }
            else:
                return {
                    "status": "error",
                    "message": "Invalid response format from price metrics API",
                    "raw_response": api_response,
                    "search_criteria": payload
                }
            
        except Exception as e:
            self.logger.error(f"Price analysis failed: {e}")
            return {
                "status": "error", 
                "message": str(e), 
                "search_criteria": payload,
                "source": "AWS_API_Gateway_PriceMetrics"
            }

class FlightBookingTool(AWSLambdaTool):
    """
    Tool for creating a flight booking order via AWS Lambda.
    This tool takes a priced flight offer and traveler details to create a final booking.
    """
    def __init__(self):
        super().__init__(
            name="flight_booking",
            description="Create a flight booking order with traveler details after a price offer has been selected.",
            endpoint="flights/booking"  # Your booking endpoint
        )

    async def execute(self, 
                     flight_offer: Dict[str, Any], 
                     travelers: List[Dict[str, Any]],
                     contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes the flight booking creation by sending a POST request to the booking API.

        Args:
            flight_offer: The single, priced flight offer object selected by the user.
            travelers: A list of traveler objects with their personal and document information.
            contacts: A list of contact details for the booking.

        Returns:
            A dictionary containing the booking confirmation details or an error.
        """
        
        self.logger.info(f"üí« Preparing to book flight offer ID: {flight_offer.get('id')}")
        self.logger.info("üîß TRIGGERING POST request to AWS API Gateway /flights/booking endpoint")

        # Construct the payload exactly according to your specified structure
        payload = {
            "data": {
                "type": "flight-order",
                "flightOffers": [flight_offer], # CRITICAL: The API expects a list of offers
                "travelers": travelers,
                "contacts": contacts,
                # Adding static remarks and ticketing agreement as per your example
                "remarks": {
                    "general": [
                        {
                            "subType": "GENERAL_MISCELLANEOUS",
                            "text": "ONLINE BOOKING VIA GEMINI AGENT"
                        }
                    ]
                },
                "ticketingAgreement": {
                    "option": "DELAY_TO_CANCEL",
                    "delay": "6D"
                }
            }
        }

        try:
            # Call the AWS API Gateway with a POST request
            result = await self._call_lambda(payload, method="POST")
            api_response = result.get("api_response", {})
            metadata = result.get("metadata", {})
            
            self.logger.info("‚úÖ Flight booking API call successful.")
            
            # Parse the booking confirmation response
            if api_response and api_response.get("success") and "data" in api_response:
                booking_data = api_response.get("data", {}).get("data", {})
                confirmation_id = booking_data.get("id")
                associated_records = booking_data.get("associatedRecords", [])
                booking_reference = "Not Found"
                if associated_records:
                    booking_reference = associated_records[0].get("reference", "Not Found")

                return {
                    "status": "success",
                    "confirmation_id": confirmation_id,
                    "booking_reference": booking_reference,
                    "message": f"Booking successfully created with reference: {booking_reference}",
                    "api_metadata": metadata,
                    "source": "AWS_API_Gateway_Booking"
                }
            else:
                self.logger.error(f"‚ùå Booking failed. Invalid response from API: {api_response}")
                return {
                    "status": "error",
                    "message": "Booking failed due to an invalid API response.",
                    "raw_response": api_response
                }

        except Exception as e:
            self.logger.error(f"‚ùå Flight booking execution failed: {e}")
            return {
                "status": "error", 
                "message": str(e), 
                "request_payload": "Payload not shown for security.",
                "source": "AWS_API_Gateway_Booking"
            }