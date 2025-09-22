#=========================
#new version with test functionality
import os
import sys

# === FORCE LOAD GOOGLE AI API KEY ===
print("🔍 Checking environment variables...")

# Check all possible environment variable names
api_key_candidates = [
    'GOOGLE_AI_API_KEY',
    'GEMINI_API_KEY', 
    'GOOGLE_API_KEY',
    'GENAI_API_KEY'
]

google_api_key = None
for key_name in api_key_candidates:
    if os.getenv(key_name):
        google_api_key = os.getenv(key_name)
        print(f"✅ Found API key in {key_name}: {google_api_key[:10]}...")
        break

if not google_api_key:
    print("❌ No Google AI API key found in environment variables!")
    print(f"📋 Checked: {api_key_candidates}")
    print("🔧 Available environment variables:")
    for key, value in os.environ.items():
        if 'API' in key.upper() or 'KEY' in key.upper():
            print(f"   {key}: {value[:10] if value else 'None'}...")

# Set the standard environment variable that ADK expects
if google_api_key:
    os.environ['GOOGLE_API_KEY'] = google_api_key
    print(f"🔧 Set GOOGLE_API_KEY for ADK")

# Now configure genai before any other imports
try:
    from google.genai import configure
    if google_api_key:
        configure(api_key=google_api_key)
        print("✅ Google GenAI configured successfully")
    else:
        print("❌ Cannot configure Google GenAI - no API key")
except Exception as e:
    print(f"❌ Google GenAI configuration failed: {e}")

import asyncio
import uuid
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import uvicorn
import json

# ADK imports - keeping as requested
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
AWS_API_KEY = 'ziU53MRcWq2FQTSDaF1sf5lK2hm9xZmR3HPYUBBD'
AWS_BASE_URL = 'https://ta2z6r502h.execute-api.ap-southeast-1.amazonaws.com/dev'

AWS_TOOLS_AVAILABLE = False
FLIGHT_SEARCH_TOOL = None
PRICE_ANALYSIS_TOOL = None
FLIGHT_PRICING_OFFERS_TOOL = None
FLIGHT_BOOKING_TOOL = None

# FIXED: Import from the correct path based on your project structure
try:
    # Based on your VS Code structure, try importing from tools directory
    current_dir = Path(__file__).parent
    tools_dir = current_dir.parent / "tools"
    sys.path.append(str(tools_dir))
    from aws_tools import FlightSearchTool as AWSFlightSearchTool
    from aws_tools import PriceAnalysisTool as AWSPriceAnalysisTool
    from aws_tools import FlightPricingOffersTool as AWSFlightPricingOffersTool
    from aws_tools import FlightBookingTool as AWSFlightBookingTool # <-- ADD THIS LINE
    print("✅ AWS flight tools imported successfully from tools folder")
    FLIGHT_SEARCH_TOOL = AWSFlightSearchTool()
    PRICE_ANALYSIS_TOOL = AWSPriceAnalysisTool()
    FLIGHT_PRICING_OFFERS_TOOL = AWSFlightPricingOffersTool()
    FLIGHT_BOOKING_TOOL = AWSFlightBookingTool()
    AWS_TOOLS_AVAILABLE = True
    logger.info("✅ AWS flight tools imported successfully")
except ImportError as e:
    print(f"❌️ Failed to import from tools/aws_tools: {e}")
    logger.warning(f"AWS tools not available: {e}")
    AWS_TOOLS_AVAILABLE = False
    
# === FLIGHT PRIORITIZATION HELPER FUNCTIONS ===

# === A2A PROTOCOL CLASSES ===

class A2AMessage(BaseModel):
    """A2A Protocol message format"""
    message: str
    context: Optional[dict] = {}
    session_id: Optional[str] = None
    user_id: Optional[str] = "user"
    metadata: Optional[dict] = {}

class A2AResponse(BaseModel):
    """A2A Protocol response format"""
    response: str
    status: str = "success"
    agent_id: str = "flight_specialist_agent"
    session_id: Optional[str] = None
    metadata: Optional[dict] = {}


def _prioritize_business_flights(flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize flights for business travel based on timing and class"""
    for flight in flights:
        score = 0
        
        # Prefer business or first class
        cabin_class = str(flight.get("cabin_class", flight.get("class", flight.get("travelClass", "")))).upper()
        if "BUSINESS" in cabin_class:
            score += 5
        elif "FIRST" in cabin_class:
            score += 7
        elif "PREMIUM" in cabin_class:
            score += 3
        
        # Prefer morning departures (6 AM - 10 AM)
        departure_time = flight.get("departure_time", flight.get("departure", {}).get("time", ""))
        if departure_time:
            try:
                if isinstance(departure_time, str):
                    hour = int(departure_time.split(':')[0]) if ':' in departure_time else 0
                    if 6 <= hour <= 10:
                        score += 2
            except (ValueError, IndexError):
                pass
        
        # Prefer direct flights
        stops = flight.get("stops", flight.get("number_of_stops", flight.get("numberOfBookableSeats", 1)))
        if stops == 0:
            score += 3
        
        # Prefer shorter duration
        duration = flight.get("duration", flight.get("flight_duration", ""))
        if duration:
            try:
                if "h" in str(duration):
                    hours = float(str(duration).split('h')[0])
                    if hours <= 8:
                        score += 2
            except (ValueError, AttributeError):
                pass
        
        flight["business_score"] = score
    
    return sorted(flights, key=lambda x: (-x.get("business_score", 0), 
                                        float(x.get("price", x.get("total_price", 999999)))))

def _prioritize_economy_flights(flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize flights for economy travel based on price and value"""
    for flight in flights:
        score = 0
        
        # Strongly prefer economy class
        cabin_class = str(flight.get("cabin_class", flight.get("class", flight.get("travelClass", "")))).upper()
        if "ECONOMY" in cabin_class:
            score += 5
        
        # Price consideration - prefer lower prices
        try:
            price = float(flight.get("price", flight.get("total_price", flight.get("grandTotal", 0))))
            if price <= 300:
                score += 4
            elif price <= 500:
                score += 3
            elif price <= 800:
                score += 2
        except (ValueError, TypeError):
            pass
        
        # Prefer reasonable departure times (avoid red-eye)
        departure_time = flight.get("departure_time", flight.get("departure", {}).get("time", ""))
        if departure_time:
            try:
                if isinstance(departure_time, str):
                    hour = int(departure_time.split(':')[0]) if ':' in departure_time else 0
                    if 7 <= hour <= 22:  # Reasonable hours
                        score += 2
            except (ValueError, IndexError):
                pass
        
        # Consider stops (some tolerance for price savings)
        stops = flight.get("stops", flight.get("number_of_stops", 1))
        if stops == 0:
            score += 2
        elif stops == 1:
            score += 1
        
        flight["economy_score"] = score
    
    return sorted(flights, key=lambda x: (-x.get("economy_score", 0), 
                                        float(x.get("price", x.get("total_price", 999999)))))

def _prioritize_family_flights(flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize flights for family travel based on convenience and timing"""
    for flight in flights:
        score = 0
        
        # Prefer direct flights for family convenience
        stops = flight.get("stops", flight.get("number_of_stops", 1))
        if stops == 0:
            score += 5
        elif stops == 1:
            score += 2
        
        # Prefer family-friendly departure times
        departure_time = flight.get("departure_time", flight.get("departure", {}).get("time", ""))
        if departure_time:
            try:
                if isinstance(departure_time, str):
                    hour = int(departure_time.split(':')[0]) if ':' in departure_time else 0
                    if 9 <= hour <= 17:  # Daytime flights
                        score += 3
            except (ValueError, IndexError):
                pass
        
        # Consider price for families
        try:
            price = float(flight.get("price", flight.get("total_price", 0)))
            if price <= 400:
                score += 3
            elif price <= 600:
                score += 2
        except (ValueError, TypeError):
            pass
        
        # Prefer reasonable duration
        duration = flight.get("duration", flight.get("flight_duration", ""))
        if duration:
            try:
                if "h" in str(duration):
                    hours = float(str(duration).split('h')[0])
                    if hours <= 10:
                        score += 2
            except (ValueError, AttributeError):
                pass
        
        flight["family_score"] = score
    
    return sorted(flights, key=lambda x: (-x.get("family_score", 0), 
                                        float(x.get("price", x.get("total_price", 999999)))))

def _process_flight_for_ai_consumption(flight: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process complex flight data into AI-friendly format based on your actual response structure
    """
    try:
        # Extract basic flight information
        flight_id = flight.get("id", "unknown")
        flight_type = flight.get("type", "flight-offer")
        source = flight.get("source", "GDS")
        
        # Extract pricing information
        price_info = flight.get("price", {})
        total_price = price_info.get("total", "0")
        currency = price_info.get("currency", "USD")
        grand_total = price_info.get("grandTotal", total_price)
        
        # Extract itinerary information
        itineraries = flight.get("itineraries", [])
        processed_itineraries = []
        
        for idx, itinerary in enumerate(itineraries):
            itinerary_type = "Outbound" if idx == 0 else "Return"
            duration = itinerary.get("duration", "Unknown")
            segments = itinerary.get("segments", [])
            
            processed_segments = []
            for segment in segments:
                departure = segment.get("departure", {})
                arrival = segment.get("arrival", {})
                
                processed_segment = {
                    "from": departure.get("iataCode", "???"),
                    "from_terminal": departure.get("terminal"),
                    "departure_time": departure.get("at", "Unknown"),
                    "to": arrival.get("iataCode", "???"), 
                    "to_terminal": arrival.get("terminal"),
                    "arrival_time": arrival.get("at", "Unknown"),
                    "airline": segment.get("carrierCode", "Unknown"),
                    "flight_number": segment.get("number", "Unknown"),
                    "aircraft": segment.get("aircraft", {}).get("code", "Unknown"),
                    "duration": segment.get("duration", "Unknown"),
                    "stops": segment.get("numberOfStops", 0)
                }
                processed_segments.append(processed_segment)
            
            processed_itineraries.append({
                "type": itinerary_type,
                "duration": duration,
                "segments": processed_segments
            })
        
        # Extract traveler pricing summary
        traveler_pricings = flight.get("travelerPricings", [])
        pricing_summary = {
            "adults": len([p for p in traveler_pricings if p.get("travelerType") == "ADULT"]),
            "children": len([p for p in traveler_pricings if p.get("travelerType") == "CHILD"]),
            "infants": len([p for p in traveler_pricings if p.get("travelerType") == "INFANT"])
        }
        
        # Extract amenities summary (simplified)
        amenities_summary = set()
        for pricing in traveler_pricings:
            for segment_detail in pricing.get("fareDetailsBySegment", []):
                for amenity in segment_detail.get("amenities", []):
                    amenity_type = amenity.get("amenityType", "Unknown")
                    is_free = not amenity.get("isChargeable", True)
                    amenities_summary.add(f"{amenity_type}{'(Free)' if is_free else '(Paid)'}")
        
        # Create AI-friendly summary
        route_summary = " → ".join([seg["from"] for seg in processed_itineraries[0]["segments"]] + 
                                  [processed_itineraries[0]["segments"][-1]["to"]])
        
        if len(processed_itineraries) > 1:
            return_route = " → ".join([seg["from"] for seg in processed_itineraries[1]["segments"]] + 
                                    [processed_itineraries[1]["segments"][-1]["to"]])
            route_summary += f" | Return: {return_route}"
        
        # Create simplified version for AI
        return {
            "id": flight_id,
            "route_summary": route_summary,
            "price": {
                "total": float(total_price),
                "currency": currency,
                "display": f"{currency} {total_price}"
            },
            "duration": {
                "outbound": processed_itineraries[0]["duration"] if processed_itineraries else "Unknown",
                "return": processed_itineraries[1]["duration"] if len(processed_itineraries) > 1 else None
            },
            "airlines": list(set([seg["airline"] for itinerary in processed_itineraries for seg in itinerary["segments"]])),
            "stops": {
                "outbound": sum([seg["stops"] for seg in processed_itineraries[0]["segments"]]) if processed_itineraries else 0,
                "return": sum([seg["stops"] for seg in processed_itineraries[1]["segments"]]) if len(processed_itineraries) > 1 else None
            },
            "travelers": pricing_summary,
            "amenities": list(amenities_summary)[:10],  # Limit to top 10 amenities
            "bookable_seats": flight.get("numberOfBookableSeats", 0),
            "instant_ticketing": flight.get("instantTicketingRequired", False),
            "last_ticketing_date": flight.get("lastTicketingDate"),
            "detailed_itineraries": processed_itineraries,  # Keep full details for detailed queries
            "_original": flight  # Keep original for reference
        }
        
    except Exception as e:
        logger.error(f"⚠️ Error processing flight {flight.get('id', 'unknown')}: {e}")
        # Return minimal version on error
        return {
            "id": flight.get("id", "unknown"),
            "route_summary": "Processing error",
            "price": {"total": 0, "currency": "USD", "display": "N/A"},
            "error": str(e),
            "_original": flight
        }

def _create_ai_friendly_summary(flights: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create an AI-friendly summary of all flight options
    """
    if not flights:
        return {
            "summary": "No flights found",
            "flights": [],
            "recommendations": []
        }
    
    # Process all flights
    processed_flights = []
    for flight in flights:
        processed_flight = _process_flight_for_ai_consumption(flight)
        processed_flights.append(processed_flight)
    
    # Create summary statistics
    prices = [f.get("price", {}).get("total", 0) for f in processed_flights if f.get("price", {}).get("total", 0) > 0]
    airlines = set()
    routes = set()
    
    for flight in processed_flights:
        if flight.get("airlines"):
            airlines.update(flight["airlines"])
        if flight.get("route_summary"):
            routes.add(flight["route_summary"].split(" | ")[0])  # Just outbound route
    
    # Calculate price statistics
    price_stats = {}
    if prices:
        prices.sort()
        price_stats = {
            "lowest": min(prices),
            "highest": max(prices),
            "average": round(sum(prices) / len(prices), 2),
            "median": prices[len(prices) // 2]
        }
    
    # Create AI recommendations
    recommendations = []
    
    if processed_flights:
        # Cheapest flight
        cheapest = min(processed_flights, key=lambda x: x.get("price", {}).get("total", float('inf')))
        recommendations.append({
            "type": "cheapest",
            "flight_id": cheapest.get("id"),
            "price": cheapest.get("price", {}).get("display"),
            "reason": "Lowest price option"
        })
        
        # Direct flights (no stops)
        direct_flights = [f for f in processed_flights if f.get("stops", {}).get("outbound", 1) == 0]
        if direct_flights:
            best_direct = min(direct_flights, key=lambda x: x.get("price", {}).get("total", float('inf')))
            recommendations.append({
                "type": "direct",
                "flight_id": best_direct.get("id"),
                "price": best_direct.get("price", {}).get("display"),
                "reason": "Direct flight, no connections"
            })
    
    return {
        "summary": {
            "total_flights": len(processed_flights),
            "airlines": list(airlines),
            "routes": list(routes),
            "price_range": price_stats
        },
        "flights": processed_flights,
        "recommendations": recommendations
    }




# === ADD THE NEW BOOKING FUNCTION AND ITS HELPERS BELOW ===
# Add these new functions before the "ADK AGENT IMPLEMENTATION" section

def _create_traveler_payload(traveler_id: str, first_name: str, last_name: str, dob: str, gender: str, email: str, phone_code: str, phone_num: str, passport_num: str, passport_expiry: str, passport_country: str, nationality: str) -> Dict[str, Any]:
    """Helper to create the traveler object for the booking payload."""
    return {
        "id": traveler_id,
        "dateOfBirth": dob,
        "name": {
            "firstName": first_name,
            "lastName": last_name
        },
        "gender": gender.upper(),
        "contact": {
            "emailAddress": email,
            "phones": [{
                "deviceType": "MOBILE",
                "countryCallingCode": phone_code,
                "number": phone_num
            }]
        },
        "documents": [{
            "documentType": "PASSPORT",
            "number": passport_num,
            "expiryDate": passport_expiry,
            "issuanceCountry": passport_country.upper(),
            "nationality": nationality.upper(),
            "holder": True
        }]
    }

def _create_contact_payload(first_name: str, last_name: str, email: str, phone_code: str, phone_num: str) -> Dict[str, Any]:
    """Helper to create the contact object for the booking payload."""
    return {
        "addresseeName": {
            "firstName": first_name,
            "lastName": last_name
        },
        "purpose": "STANDARD",
        "phones": [{
            "deviceType": "MOBILE",
            "countryCallingCode": phone_code,
            "number": phone_num
        }],
        "emailAddress": email
    }


# === DIRECT API GATEWAY FUNCTIONS ===

async def _make_direct_flight_api_call(origin: str, destination: str, departure_date: str, 
                                     return_date: Optional[str] = None, adults: int = 1, 
                                     children: int = 0, infants: int = 0, cabin_class: str = "ECONOMY",
                                     currency_code: str = "USD") -> Dict[str, Any]:
    """
    FIXED: Make direct API call to AWS API Gateway for flight search using GET with URL parameters
    Following the pattern: GET /flights/search?originLocationCode=JFK&destinationLocationCode=MAD&departureDate=2025-07-15...
    """
    
    # FIXED: Use GET with URL parameters as requested
    api_url = f"{AWS_BASE_URL}/flights/search"  # Your actual flight search endpoint
        
    # FIXED: All parameters go in the URL as query parameters (GET method)
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(), 
        "departureDate": departure_date,
        "adults": str(adults),
        "travelClass": cabin_class.upper(),
        "currencyCode": currency_code.upper()
    }
    
    # Add optional parameters only if provided
    if return_date:
        params["returnDate"] = return_date
    if children > 0:
        params["children"] = str(children)
    if infants > 0:
        params["infants"] = str(infants)
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if AWS_API_KEY:
        headers['x-api-key'] = AWS_API_KEY
    
    try:
        logger.info(f"🌐 Making direct API Gateway call to: {api_url}")
        logger.info(f"📋 Request parameters: {params}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # FIXED: Use GET method with parameters in URL
            response = await client.get(api_url, params=params, headers=headers)
            
            logger.info(f"📡 API Gateway response status: {response.status_code}")
            logger.infor(f"Response Test Result: {response}")
            # FIXED: Better error handling
            if response.status_code != 200:
                logger.error(f"❌ API Gateway error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "error_message": f"API Gateway returned {response.status_code}: {response.text}",
                    "flights": []
                }
            
            response.raise_for_status()
            api_response = response.json()
            
            logger.info(f"✅ API Gateway response received successfully")
            
            # FIXED: Handle different response structures from your API
            flights = []
            if isinstance(api_response, dict):
                # Try different possible response keys from Amadeus API
                for key in ["data", "flights", "results", "body", "offers"]:
                    if key in api_response:
                        flights = api_response[key]
                        break
                # If it's a direct flight list in the dict
                if not flights and "origin" in api_response:
                    flights = [api_response]
            elif isinstance(api_response, list):
                flights = api_response
            
            logger.info(f"✈️ Extracted {len(flights)} flights from API response")
            
            return {
                "status": "success",
                "flights": flights,
                "total_results": len(flights),
                "api_gateway_triggered": True,
                "source": "AWS_API_Gateway_Direct_GET",
                "request_method": "GET",
                "request_url": f"{api_url}?{httpx._utils.build_url_string(params, encoding=None)}"
            }
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ API Gateway HTTP error: {e.response.status_code} - {e.response.text}")
        return {
            "status": "error",
            "error_message": f"API Gateway HTTP error {e.response.status_code}: {e.response.text}",
            "flights": [],
            "api_gateway_triggered": False
        }
    except httpx.TimeoutException:
        logger.error(f"❌ API Gateway timeout after 30 seconds")
        return {
            "status": "error",
            "error_message": "API Gateway request timed out after 30 seconds",
            "flights": [],
            "api_gateway_triggered": False
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error calling API Gateway: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
            "flights": [],
            "api_gateway_triggered": False
        }

# === ADK FUNCTION TOOLS ===

async def flight_search(origin: str, destination: str, departure_date: str, 
                       return_date: str, adults: int, children: int, 
                       infants: int, cabin_class: str, 
                       currency_code: str, travel_type: str) -> Dict[str, Any]:
    """
    ENHANCED: Search for flights and return AI-friendly processed data
    """
    
    logger.info("✈️ ADK FUNCTION TOOL: flight_search called")
    logger.info(f"🌍 Parameters: {origin} -> {destination}, {departure_date}, {adults} adults")
    
    # Parameter validation
    if not origin or len(origin) != 3:
        return {
            "status": "error",
            "error_message": f"Invalid origin airport code: {origin}. Must be 3 letters (e.g., JFK, LAX, SYD).",
            "flights": []
        }
    
    if not destination or len(destination) != 3:
        return {
            "status": "error", 
            "error_message": f"Invalid destination airport code: {destination}. Must be 3 letters (e.g., JFK, LAX, SYD).",
            "flights": []
        }
    
    if not departure_date:
        return {
            "status": "error",
            "error_message": "Departure date is required in YYYY-MM-DD format.",
            "flights": []
        }
    
    # Try existing AWS tool first
    if AWS_TOOLS_AVAILABLE and FLIGHT_SEARCH_TOOL:
        logger.info("🔧 Using existing FlightSearchTool to trigger AWS API Gateway")
        
        try:
            result = await FLIGHT_SEARCH_TOOL.execute(
                origin=origin.upper(),
                destination=destination.upper(),
                departure_date=departure_date,
                return_date=return_date,
                adults=adults,
                children=children,
                infants=infants,
                cabin_class=cabin_class,
                currency_code=currency_code
            )
            
            logger.info(f"✅ FlightSearchTool executed successfully")
            logger.info(f"✈️ Result status: {result.get('status')} - {len(result.get('flights', []))} flights found")
            
            # ENHANCED: Process complex flight data for AI consumption
            raw_flights = result.get("flights", [])
            if raw_flights:
                logger.info("🧠 Processing complex flight data for AI consumption...")
                
                # Create AI-friendly summary
                ai_friendly_data = _create_ai_friendly_summary(raw_flights)
                
                logger.info(f"✅ Processed {len(ai_friendly_data['flights'])} flights for AI")
                
                return {
                    "status": result.get("status", "success"),
                    "flights": ai_friendly_data["flights"],  # AI-processed flights
                    "summary": ai_friendly_data["summary"],   # Summary statistics
                    "recommendations": ai_friendly_data["recommendations"],  # AI recommendations
                    "total_results": len(raw_flights),
                    "search_criteria": {
                        "origin": origin.upper(),
                        "destination": destination.upper(),
                        "departure_date": departure_date,
                        "return_date": return_date,
                        "passengers": {
                            "adults": adults,
                            "children": children,
                            "infants": infants
                        },
                        "cabin_class": cabin_class,
                        "currency": currency_code,
                        "travel_type": travel_type
                    },
                    "api_gateway_triggered": True,
                    "tool_used": "existing_FlightSearchTool_with_AI_processing",
                    "source": "AWS_API_Gateway_Amadeus_GDS",
                    "trip_type": "round_trip" if return_date else "one_way",
                    "ai_processed": True
                }
            else:
                return {
                    "status": "success",
                    "flights": [],
                    "summary": {"total_flights": 0},
                    "recommendations": [],
                    "total_results": 0,
                    "message": "No flights found for your search criteria"
                }
            
        except Exception as e:
            logger.error(f"❌ FlightSearchTool execution failed: {e}")
            logger.info("🔄 Falling back to direct API Gateway call")
    
    # Fallback to direct API call
    logger.info("🔄 Using direct API Gateway call with GET method")
    result = await _make_direct_flight_api_call(
        origin, destination, departure_date, return_date, 
        adults, children, infants, cabin_class, currency_code
    )
    
    # Process direct API results the same way
    if result.get("status") == "success" and result.get("flights"):
        raw_flights = result["flights"]
        ai_friendly_data = _create_ai_friendly_summary(raw_flights)
        
        result.update({
            "flights": ai_friendly_data["flights"],
            "summary": ai_friendly_data["summary"],
            "recommendations": ai_friendly_data["recommendations"],
            "ai_processed": True
        })
    
    return result


async def flight_price_analysis(flights: List[Dict[str, Any]], 
                               budget_max: Optional[float] = None,
                               preferred_airlines: Optional[List[str]] = None,
                               travel_type: str = "economy") -> Dict[str, Any]:
    """
    FIXED: Analyze flight prices and provide recommendations.
    """
    
    logger.info("💰 ADK FUNCTION TOOL: flight_price_analysis called")
    logger.info(f"✈️ Analyzing {len(flights)} flights for {travel_type} travel")
    
    if not flights:
        return {
            "status": "no_data",
            "error_message": "No flight data provided for analysis",
            "analysis": {}
        }
    
    # FIXED: Use existing analysis tool if available
    if AWS_TOOLS_AVAILABLE and PRICE_ANALYSIS_TOOL:
        logger.info("🔧 Using your existing PriceAnalysisTool")
        
        try:
            analysis_criteria = {
                "travel_type": travel_type
            }
            if budget_max:
                analysis_criteria["budget_max"] = budget_max
            if preferred_airlines:
                analysis_criteria["preferred_airlines"] = preferred_airlines
            
            result = await PRICE_ANALYSIS_TOOL.execute(options=flights, criteria=analysis_criteria)
            
            logger.info(f"✅ Price analysis completed using existing AWS tool")
            
            return {
                "status": result.get("status", "success"),
                "analysis": result.get("analysis", {}),
                "recommendations": result.get("recommendations", []),
                "flight_count": len(flights),
                "criteria_applied": {
                    "budget_max": budget_max,
                    "preferred_airlines": preferred_airlines,
                    "travel_type": travel_type
                },
                "tool_used": "existing_PriceAnalysisTool"
            }
            
        except Exception as e:
            logger.error(f"❌ PriceAnalysisTool execution failed: {e}")
            # Fall through to fallback analysis
    
    # FIXED: Improved fallback price analysis
    logger.info("🔄 Using fallback price analysis")
    
    try:
        prices = []
        airlines = {}
        cabin_classes = {}
        
        for flight in flights:
            # Extract price information with multiple fallback keys
            price = None
            price_keys = ["price", "total_price", "amount", "cost", "fare", "grandTotal"]
            
            for key in price_keys:
                if key in flight:
                    price_info = flight[key]
                    if isinstance(price_info, dict):
                        # Handle nested price objects
                        for subkey in ["total", "amount", "value", "price", "grandTotal"]:
                            if subkey in price_info:
                                try:
                                    price = float(price_info[subkey])
                                    break
                                except (ValueError, TypeError):
                                    continue
                    elif isinstance(price_info, (int, float)):
                        price = float(price_info)
                    elif isinstance(price_info, str):
                        try:
                            # Remove currency symbols and parse
                            price_clean = ''.join(c for c in price_info if c.isdigit() or c == '.')
                            if price_clean:
                                price = float(price_clean)
                        except ValueError:
                            continue
                    
                    if price is not None:
                        break
            
            if price is not None:
                prices.append(price)
            
            # Extract airline information
            airline = flight.get("airline", flight.get("carrier", flight.get("airline_code", flight.get("validatingAirlineCodes", ["Unknown"]))))
            if isinstance(airline, list) and airline:
                airline = airline[0]
            airlines[str(airline)] = airlines.get(str(airline), 0) + 1
            
            # Extract cabin class information
            cabin = flight.get("cabin_class", flight.get("class", flight.get("travel_class", flight.get("travelClass", "Economy"))))
            cabin_classes[str(cabin)] = cabin_classes.get(str(cabin), 0) + 1
        
        if not prices:
            return {
                "status": "no_prices",
                "error_message": "No valid price data found in the provided flights",
                "analysis": {}
            }
        
        # Calculate statistics
        prices.sort()
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        median_price = prices[len(prices)//2]
        
        # Calculate quartiles
        q1_idx = len(prices) // 4
        q3_idx = (3 * len(prices)) // 4
        q1_price = prices[q1_idx] if q1_idx < len(prices) else min_price
        q3_price = prices[q3_idx] if q3_idx < len(prices) else max_price
        
        # Generate recommendations
        recommendations = []
        
        # Find best value (cheapest option)
        cheapest_flights = [i for i, flight in enumerate(flights) 
                          if any(str(min_price) in str(flight.get(key, "")) for key in price_keys)]
        if cheapest_flights:
            recommendations.append({
                "type": "cheapest_option",
                "flight_indices": cheapest_flights[:3],  # Top 3 cheapest
                "price": min_price,
                "reason": f"Lowest price option at ${min_price:.2f}"
            })
        
        # Budget filter recommendations
        if budget_max:
            budget_flights = [price for price in prices if price <= budget_max]
            if budget_flights:
                recommendations.append({
                    "type": "within_budget",
                    "count": len(budget_flights),
                    "percentage": (len(budget_flights) / len(prices)) * 100,
                    "max_budget": budget_max,
                    "reason": f"{len(budget_flights)} flights ({(len(budget_flights)/len(prices))*100:.1f}%) within budget of ${budget_max:.2f}"
                })
        
        # Best value recommendation (good price in middle range)
        mid_range_flights = [price for price in prices if q1_price <= price <= median_price]
        if mid_range_flights:
            recommendations.append({
                "type": "best_value",
                "price_range": f"${q1_price:.2f} - ${median_price:.2f}",
                "count": len(mid_range_flights),
                "reason": f"Good balance of price and quality in the ${q1_price:.2f}-${median_price:.2f} range"
            })
        
        # Airline preferences
        if preferred_airlines:
            airline_recommendations = []
            for airline in preferred_airlines:
                matching_airlines = [a for a in airlines.keys() if airline.lower() in str(a).lower()]
                for matching_airline in matching_airlines:
                    if airlines[matching_airline] > 0:
                        airline_recommendations.append({
                            "airline": matching_airline,
                            "count": airlines[matching_airline],
                            "reason": f"{airlines[matching_airline]} flights available from preferred airline {matching_airline}"
                        })
            recommendations.extend(airline_recommendations)
        
        return {
            "status": "success",
            "analysis": {
                "price_statistics": {
                    "min_price": min_price,
                    "max_price": max_price,
                    "average_price": round(avg_price, 2),
                    "median_price": median_price,
                    "q1_price": q1_price,
                    "q3_price": q3_price,
                    "total_options": len(prices),
                    "price_range": round(max_price - min_price, 2),
                    "std_deviation": round((sum((p - avg_price) ** 2 for p in prices) / len(prices)) ** 0.5, 2)
                },
                "airline_distribution": airlines,
                "cabin_class_distribution": cabin_classes,
                "total_airlines": len(airlines),
                "flight_count": len(flights),
                "price_distribution": {
                    "budget": len([p for p in prices if p < avg_price * 0.8]),
                    "mid_range": len([p for p in prices if avg_price * 0.8 <= p <= avg_price * 1.2]),
                    "premium": len([p for p in prices if p > avg_price * 1.2])
                }
            },
            "recommendations": recommendations,
            "criteria_applied": {
                "budget_max": budget_max,
                "preferred_airlines": preferred_airlines,
                "travel_type": travel_type
            },
            "tool_used": "enhanced_fallback_analysis"
        }
        
    except Exception as e:
        logger.error(f"❌ Fallback price analysis failed: {e}")
        return {
            "status": "error",
            "error_message": f"Price analysis failed: {str(e)}",
            "analysis": {}
        }
        
        # === A2A FASTAPI APPLICATION ===
        
def create_flight_specialist_agent():
    """Create Flight Specialist Agent with A2A compatibility"""
    
    logger.info("✈️ Creating Flight Specialist Agent with ADK Function Tools")
    
    agent = LlmAgent(
        name="flight_specialist_agent",
        model="gemini-2.0-flash",
        tools=[flight_search, flight_price_analysis],
        instruction="""You are an Expert Flight Specialist with direct access to live flight inventory through AWS API Gateway and Amadeus GDS integration.

🔧 CRITICAL FUNCTION USAGE:
1. For ANY flight inquiry: IMMEDIATELY execute flight_search() with proper parameters:
   - origin: Airport code (e.g., JFK, LAX, SFO)
   - destination: Airport code (e.g., LHR, CDG, SIN)
   - departure_date: YYYY-MM-DD format
   - return_date: YYYY-MM-DD format (for round trips)
   - adults: Number of adult passengers
   - children: Number of children (2-11 years)
   - infants: Number of infants (0-2 years)
   - cabin_class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST
   - currency_code: USD, EUR, GBP
   - travel_type: economy, business, first

2. Present results in professional aviation format with complete flight details

📋 FLIGHT DISPLAY FORMAT:
After calling flight_search(), present each flight exactly like this:

✈️ **[Airline Name]** - Flight [Number]
🛫 **Departure:** [Airport] ([Code]) at [Time]
🛬 **Arrival:** [Airport] ([Code]) at [Time]
⏱️ **Duration:** [Hours]h [Minutes]m
💺 **Cabin:** [Class]
💰 **Price:** [Amount] [Currency]
🎟️ **Availability:** [Status]

📍 SMART PARAMETER PROCESSING:
• Convert cities to airport codes: New York→JFK/EWR, London→LHR, Paris→CDG
• Parse dates: "October 10-15" → departure="2025-10-10", return="2025-10-15"
• Extract passengers: "2 adults, 1 child" → adults=2, children=1
• Determine cabin class from context: "business class" → BUSINESS

🎯 PROFESSIONAL RESPONSE STRUCTURE:
1. Start with: "I've found [X] flights using live AWS API Gateway data..."
2. Present best options based on:
   - Price and value
   - Flight duration and stops
   - Airline reliability
   - Departure/arrival times
3. Include connection details if applicable
4. Provide fare rules and booking requirements
5. Suggest alternatives if needed

⚠️ QUALITY STANDARDS:
• NEVER show raw data structures or JSON
• ALWAYS maintain professional aviation industry tone
• PROVIDE actionable recommendations with:
  - Fare comparisons
  - Schedule options
  - Booking requirements
  - Travel tips

🌟 EXPERTISE AREAS:
• Flight routing optimization
• Fare class recommendations
• Connection timing analysis
• Airport and airline knowledge
• Travel requirements guidance

Remember: You're providing expert aviation consulting with live flight data backing your recommendations. Always prioritize accurate, helpful, and professional responses.
        """,
        description="A2A-enabled flight specialist with AWS API Gateway integration"
    )
    
    logger.info("✅ Flight Specialist Agent created with A2A compatibility")
    return agent

# Create agent instances
flight_specialist_agent = create_flight_specialist_agent()
agent = flight_specialist_agent
root_agent = flight_specialist_agent


app = FastAPI(
    title="Flight Specialist Agent - A2A Enabled",
    version="1.2.0",
    description="A2A-enabled flight specialist with AWS API Gateway integration"
)

# Create alias for uvicorn
a2a_app = app

# === A2A ENDPOINTS ===

@app.post("/chat") 
async def a2a_chat_endpoint(message_data: A2AMessage):
    """A2A Main chat endpoint for flight requests"""
    try:
        logger.info(f"🔗 A2A chat request received: {message_data.message}")
        
        # Create ADK session for agent interaction
        session_service = InMemorySessionService()
        runner = Runner(
            agent=flight_specialist_agent, 
            app_name="flight_a2a_app", 
            session_service=session_service
        )
        
        session_id = message_data.session_id or f"a2a_session_{uuid.uuid4()}"
        user_id = message_data.user_id or "a2a_user"
        
        # Create session
        await session_service.create_session(
            app_name="flight_a2a_app", 
            user_id=user_id, 
            session_id=session_id
        )
        
        # Process message through ADK agent
        content = types.Content(
            role='user', 
            parts=[types.Part(text=message_data.message)]
        )
        
        response_text = ""
        function_calls_made = []
        
        # Run agent and collect response
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=session_id, 
            new_message=content
        ):
            if event.get_function_calls():
                for call in event.get_function_calls():
                    function_calls_made.append(call.name)
                    logger.info(f"🔧 A2A triggered function: {call.name}")
            
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text.strip()
        
        return A2AResponse(
            response=response_text,
            status="success",
            agent_id="flight_specialist_agent",
            session_id=session_id,
            metadata={
                "functions_called": function_calls_made,
                "processing_time": datetime.now().isoformat(),
                "aws_integration": "active" if AWS_TOOLS_AVAILABLE else "demo_mode"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ A2A chat endpoint error: {e}")
        return A2AResponse(
            response=f"I encountered an error processing your flight request: {str(e)}. Please try again.",
            status="error",
            agent_id="flight_specialist_agent",
            metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
        )

@app.post("/flight/search")
async def direct_flight_search_endpoint(search_request: dict):
    """Direct flight search endpoint for A2A integration"""
    try:
        # Extract search parameters
        origin = search_request.get("origin")
        destination = search_request.get("destination")
        departure_date = search_request.get("departureDate")
        return_date = search_request.get("returnDate", "")
        adults = search_request.get("adults", 1)
        children = search_request.get("children", 0)
        infants = search_request.get("infants", 0)
        cabin_class = search_request.get("cabinClass", "ECONOMY")
        currency_code = search_request.get("currencyCode", "USD")
        travel_type = search_request.get("travelType", "economy")
        
        if not all([origin, destination, departure_date]):
            raise HTTPException(
                status_code=400, 
                detail="origin, destination, and departureDate are required"
            )
        
        # Call flight search function
        result = await flight_search(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            children=children,
            infants=infants,
            cabin_class=cabin_class,
            currency_code=currency_code,
            travel_type=travel_type
        )
        
        return {
            "status": "success",
            "data": result,
            "agent": "flight_specialist_agent",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Direct flight search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """A2A Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "flight_specialist_agent",
        "version": "1.2.0",
        "a2a_enabled": True,
        "aws_tools_available": AWS_TOOLS_AVAILABLE,
        "simplified_mode": True,
        "timestamp": datetime.now().isoformat()
    }

# === A2A SERVER MANAGEMENT ===

async def start_a2a_server():
    """Start the A2A-enabled flight specialist server"""
    
    print("🚀 Starting Flight Specialist Agent with A2A Protocol Support")
    print("=" * 70)
    print(f"🔗 A2A Agent Card: http://localhost:8003/.well-known/agent_card")
    print(f"💬 A2A Chat Endpoint: http://localhost:8003/chat") 
    print(f"✈️ Direct Flight Search: http://localhost:8003/flight/search")
    print(f"❤️ Health Check: http://localhost:8003/health")
    print("=" * 70)
    
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=8003,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def test_a2a_integration():
    """Test A2A integration"""
    print("🧪 Testing A2A Integration")
    
    # Create test client
    async with httpx.AsyncClient() as client:
        # Test 1: Agent discovery
        print("\n1. Testing agent discovery...")
        response = await client.get("http://localhost:8003/.well-known/agent_card")
        print(f"✅ Agent card status: {response.status_code}")
        
        # Test 2: Chat endpoint
        print("\n2. Testing chat endpoint...")
        test_message = {
            "message": "Find flights from JFK to LAX on October 10, 2025",
            "context": {"travel_type": "economy"},
            "session_id": "test_session"
        }
        response = await client.post("http://localhost:8003/chat", json=test_message)
        print(f"✅ Chat response status: {response.status_code}")
        
        # Test 3: Direct search
        print("\n3. Testing direct flight search...")
        search_request = {
            "origin": "JFK",
            "destination": "LAX",
            "departureDate": "2025-10-10",
            "adults": 1,
            "cabinClass": "ECONOMY"
        }
        response = await client.post("http://localhost:8003/flight/search", json=search_request)
        print(f"✅ Search response status: {response.status_code}")

# === MAIN EXECUTION ===

async def main():
    """Main execution function"""
    print("✈️ Flight Specialist Agent - A2A Enabled")
    print("Choose execution mode:")
    print("1. Start A2A Server")
    print("2. Test A2A Integration")
    
    try:
        mode = input("Enter choice (1-2): ").strip()
    except:
        mode = "1"
    
    if mode == "1":
        await start_a2a_server()
    elif mode == "2":
        await test_a2a_integration()
    else:
        await start_a2a_server()

if __name__ == "__main__":
    asyncio.run(main())
