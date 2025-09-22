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
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta
import httpx
import json
from dotenv import load_dotenv

# FastAPI and Pydantic imports for A2A
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# ADK imports
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

# Try to import AWS tools
AWS_TOOLS_AVAILABLE = False

try:
    current_dir = Path(__file__).parent
    tools_dir = current_dir.parent / "tools"
    sys.path.append(str(tools_dir))
    from aws_tools import HotelSearchTool as AWSHotelSearchTool
    from aws_tools import HotelGeocodeSearchTool as AWSHotelGeocodeSearchTool
    from aws_tools import HotelBookingTool as AWSHotelBookingTool
    HOTEL_BOOKING_TOOL = AWSHotelBookingTool()
    HOTEL_GEOCODE_SEARCH_TOOL = AWSHotelGeocodeSearchTool()
    HOTEL_SEARCH_TOOL = AWSHotelSearchTool()
    AWS_TOOLS_AVAILABLE = True
    logger.info("✅ AWS tools imported successfully")
except ImportError as e:
    logger.warning(f"⚠️ AWS tools not available: {e}")
    AWS_TOOLS_AVAILABLE = False

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
    agent_id: str = "hotel_specialist_agent"
    session_id: Optional[str] = None
    metadata: Optional[dict] = {}

# === HARDCODED LOCATION DATABASE ===

class HardcodedLocationDatabase:
    """Complete hardcoded coordinates database for global hotel locations"""
    
    def __init__(self):
        self.city_coordinates = {
            # Major European Cities
            "PAR": (48.8566, 2.3522),    # Paris, France
            "LON": (51.5074, -0.1278),   # London, UK
            "ROM": (41.9028, 12.4964),   # Rome, Italy
            "BCN": (41.3851, 2.1734),    # Barcelona, Spain
            "MAD": (40.4168, -3.7038),   # Madrid, Spain
            "BER": (52.5200, 13.4050),   # Berlin, Germany
            "MUC": (48.1351, 11.5820),   # Munich, Germany
            "AMS": (52.3676, 4.9041),    # Amsterdam, Netherlands
            "ZUR": (47.3769, 8.5417),    # Zurich, Switzerland
            "VIE": (48.2082, 16.3738),   # Vienna, Austria
            
            # North American Cities
            "NYC": (40.7128, -74.0060),  # New York City, USA
            "LAX": (34.0522, -118.2437), # Los Angeles, USA
            "CHI": (41.8781, -87.6298),  # Chicago, USA
            "MIA": (25.7617, -80.1918),  # Miami, USA
            "LAS": (36.1699, -115.1398), # Las Vegas, USA
            "SFO": (37.7749, -122.4194), # San Francisco, USA
            "BOS": (42.3601, -71.0589),  # Boston, USA
            "TOR": (43.6532, -79.3832),  # Toronto, Canada
            "VAN": (49.2827, -123.1207), # Vancouver, Canada
            
            # Asian Cities
            "TYO": (35.6762, 139.6503),  # Tokyo, Japan
            "OSA": (34.6937, 135.5023),  # Osaka, Japan
            "SEL": (37.5665, 126.9780),  # Seoul, South Korea
            "BEI": (39.9042, 116.4074),  # Beijing, China
            "SHA": (31.2304, 121.4737),  # Shanghai, China
            "HKG": (22.3193, 114.1694),  # Hong Kong
            "SIN": (1.3521, 103.8198),   # Singapore
            "KUL": (3.1390, 101.6869),   # Kuala Lumpur, Malaysia
            "BKK": (13.7563, 100.5018),  # Bangkok, Thailand
            "MNL": (14.5995, 120.9842),  # Manila, Philippines
            "JKT": (6.2088, 106.8456),   # Jakarta, Indonesia
            "DEL": (28.7041, 77.1025),   # Delhi, India
            "BOM": (19.0760, 72.8777),   # Mumbai, India
            "DXB": (25.2048, 55.2708),   # Dubai, UAE
            
            # Australian & Oceanian Cities
            "SYD": (-33.8688, 151.2093), # Sydney, Australia
            "MEL": (-37.8136, 144.9631), # Melbourne, Australia
            "BNE": (-27.4698, 153.0251), # Brisbane, Australia
            "AKL": (-36.8485, 174.7633), # Auckland, New Zealand
            
            # South American Cities
            "SAO": (-23.5505, -46.6333), # São Paulo, Brazil
            "RIO": (-22.9068, -43.1729), # Rio de Janeiro, Brazil
            "BUE": (-34.6118, -58.3960), # Buenos Aires, Argentina
            "SCL": (-33.4489, -70.6693), # Santiago, Chile
            "LIM": (-12.0464, -77.0428), # Lima, Peru
            
            # African Cities
            "CAI": (30.0444, 31.2357),   # Cairo, Egypt
            "JNB": (-26.2041, 28.0473),  # Johannesburg, South Africa
            "CPT": (-33.9249, 18.4241),  # Cape Town, South Africa
        }
        
        self.city_name_to_code = {
            # Europe
            "paris": "PAR", "london": "LON", "rome": "ROM", "barcelona": "BCN",
            "madrid": "MAD", "berlin": "BER", "munich": "MUC", "amsterdam": "AMS",
            "zurich": "ZUR", "vienna": "VIE",
            
            # North America
            "new york": "NYC", "new york city": "NYC", "nyc": "NYC", "manhattan": "NYC",
            "los angeles": "LAX", "la": "LAX", "chicago": "CHI", "miami": "MIA",
            "las vegas": "LAS", "vegas": "LAS", "san francisco": "SFO", "sf": "SFO",
            "boston": "BOS", "toronto": "TOR", "vancouver": "VAN",
            
            # Asia
            "tokyo": "TYO", "osaka": "OSA", "seoul": "SEL", "beijing": "BEI",
            "shanghai": "SHA", "hong kong": "HKG", "singapore": "SIN",
            "kuala lumpur": "KUL", "bangkok": "BKK", "manila": "MNL",
            "jakarta": "JKT", "delhi": "DEL", "mumbai": "BOM", "bombay": "BOM",
            "dubai": "DXB",
            
            # Australia & Oceania
            "sydney": "SYD", "melbourne": "MEL", "brisbane": "BNE",
            "auckland": "AKL",
            
            # South America
            "sao paulo": "SAO", "são paulo": "SAO", "rio de janeiro": "RIO", "rio": "RIO",
            "buenos aires": "BUE", "santiago": "SCL", "lima": "LIM",
            
            # Africa
            "cairo": "CAI", "johannesburg": "JNB", "cape town": "CPT",
        }
    
    def get_coordinates(self, location_input: str) -> tuple[float, float]:
        """Get coordinates for any location input"""
        location = location_input.strip().upper()
        location_lower = location_input.strip().lower()
        
        # Method 1: Direct city code lookup
        if location in self.city_coordinates:
            return self.city_coordinates[location]
        
        # Method 2: City name lookup
        if location_lower in self.city_name_to_code:
            city_code = self.city_name_to_code[location_lower]
            return self.city_coordinates[city_code]
        
        # Method 3: Partial matching
        for city_name, city_code in self.city_name_to_code.items():
            if location_lower in city_name or city_name in location_lower:
                return self.city_coordinates[city_code]
        
        # Default to Paris if no match found
        return self.city_coordinates["PAR"]
    
    def get_city_info(self, location_input: str) -> dict:
        """Get comprehensive city information"""
        coords = self.get_coordinates(location_input)
        location_lower = location_input.strip().lower()
        
        # Find the city code
        city_code = "PAR"  # default
        if location_input.upper() in self.city_coordinates:
            city_code = location_input.upper()
        elif location_lower in self.city_name_to_code:
            city_code = self.city_name_to_code[location_lower]
        
        return {
            "city_code": city_code,
            "coordinates": coords,
            "latitude": coords[0],
            "longitude": coords[1],
            "original_input": location_input
        }

# Create global location database instance
location_db = HardcodedLocationDatabase()

async def _make_direct_api_call(cityCode: str, latitude: float, longitude: float, 
                               checkIn: str, checkOut: str, adults: int, children: int,
                               radius: int, radiusUnit: str, chainCodes: str, 
                               amenities: str, ratings: str, hotelSource: str,
                               pageLimit: int, pageOffset: int) -> Dict[str, Any]:
    """Make direct API call to AWS API Gateway"""
    
    api_url = f"{AWS_BASE_URL}/hotels/geocode"
    
    params = {
        "cityCode": cityCode.upper(),
        "latitude": str(latitude),
        "longitude": str(longitude),
        "radius": str(radius),
        "radiusUnit": radiusUnit,
        "adults": str(adults),
        "children": str(children),
        "chainCodes": chainCodes,
        "amenities": amenities,
        "ratings": ratings,
        "hotelSource": hotelSource,
        "checkIn": checkIn,
        "checkOut": checkOut,
        "pageLimit": str(pageLimit),
        "pageOffset": str(max(pageOffset, 0))
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if AWS_API_KEY:
        headers['x-api-key'] = AWS_API_KEY
    
    try:
        logger.info(f"🔌 Making direct API Gateway call to: {api_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, params=params, headers=headers)
            
            logger.info(f"📡 API Gateway response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"❌ API Gateway error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "error_message": f"API Gateway returned {response.status_code}",
                    "hotels": []
                }
            
            api_response = response.json()
            
            logger.info(api_response)
            
            # Extract hotels from response
            hotels = []
            if isinstance(api_response, dict):
                for key in ["data", "hotels", "results", "body"]:
                    if key in api_response:
                        hotels = api_response[key]
                        break
            elif isinstance(api_response, list):
                hotels = api_response
            
            logger.info(f"🏨 Extracted {len(hotels)} hotels from API response")
            
            return {
                "status": "success",
                "hotels": hotels,
                "total_results": len(hotels),
                "api_gateway_triggered": True,
                "source": "AWS_API_Gateway_Direct"
            }
            
    except Exception as e:
        logger.error(f"❌ Direct API call failed: {str(e)}")
        return {
            "status": "error",
            "error_message": f"API call failed: {str(e)}",
            "hotels": []
        }
        
async def _make_direct_api_call_search(hotelIds: str, checkInDate: str, checkOutDate: str, adults: int) -> Dict[str, Any]:
    """Make direct API call to AWS API Gateway"""
    
    api_url = f"{AWS_BASE_URL}/hotels/search"
    
    params = {
        "hotelIds": hotelIds,
        "adults": str(adults),
        "checkInDate": checkInDate,
        "checkOutDate": checkOutDate,
    }
    
    logger.info(f"Params: {params}")
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if AWS_API_KEY:
        headers['x-api-key'] = AWS_API_KEY
    
    try:
        logger.info(f"🔌 Making direct API Gateway call to: {api_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url, params=params, headers=headers)
            
            logger.info(f"📡 API Gateway response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"❌ API Gateway error: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "error_message": f"API Gateway returned {response.status_code}",
                    "hotels": []
                }
            
            api_response = response.json()
            
            logger.info(f"API Response: {api_response}")
            
            # Extract hotels from response
            offers = api_response.get("offers", "")
            
            logger.info(f"Offers {offers}")
            
            # logger.info(f"🏨 Extracted {len(hotels)} hotels from API response")
            
            return {
                "status": "success",
                "offers": offers,
                "total_results": len(offers),
                "api_gateway_triggered": True,
                "source": "AWS_API_Gateway_Direct"
            }
            
    except Exception as e:
        logger.error(f"❌ Direct API call failed: {str(e)}")
        return {
            "status": "error",
            "error_message": f"API call failed: {str(e)}",
            "hotels": []
        }

# === MOCK DATA HELPER ===

async def _get_mock_hotels(cityCode: str, checkIn: str, checkOut: str, 
                          adults: int, children: int, tripType: str) -> Dict[str, Any]:
    """Generate mock hotel data when API fails"""
    
    city_names = {
        "PAR": "Paris", "SIN": "Singapore", "LON": "London", "NYC": "New York",
        "TYO": "Tokyo", "DXB": "Dubai", "BKK": "Bangkok", "SYD": "Sydney"
    }
    city_name = city_names.get(cityCode, cityCode)
    
    mock_hotels = [
        {
            "name": f"Grand Hotel {city_name}",
            "location": f"{city_name} City Center",
            "price": 280,
            "currency": "USD",
            "rating": 4.3,
            "amenities": ["WiFi", "Pool", "Restaurant", "Spa"],
            "description": f"Luxury hotel in the heart of {city_name}",
            "availability": "Available"
        },
        {
            "name": f"Business Inn {city_name}",
            "location": f"{city_name} Downtown", 
            "price": 180,
            "currency": "USD",
            "rating": 4.0,
            "amenities": ["WiFi", "Business Center", "Gym", "Airport Shuttle"],
            "description": f"Modern business hotel in {city_name}",
            "availability": "Available"
        },
        {
            "name": f"Family Hotel {city_name}",
            "location": f"{city_name} Suburbs",
            "price": 150,
            "currency": "USD",
            "rating": 3.8,
            "amenities": ["WiFi", "Pool", "Kids Club", "Family Rooms"],
            "description": f"Family-friendly hotel in {city_name}",
            "availability": "Available"
        }
    ]
    
    return {
        "status": "success",
        "hotels": mock_hotels,
        "total_results": len(mock_hotels),
        "api_gateway_triggered": False,
        "source": "Mock_Data",
        "note": f"Demo data for {city_name} - API Gateway not responding"
    }

# === COMPLETELY FIXED HOTEL SEARCH FUNCTION ===

async def hotel_booking(hotelOfferId: str, primary_guest_title: str, primary_guest_firstName: str, 
                       primary_guest_lastName: str, primary_guest_email: str, primary_guest_phone: str,
                       payment_vendorCode: str, payment_cardNumber: str, payment_expiryDate: str, 
                       payment_holderName: str, travel_agent_email: str = "") -> Dict[str, Any]:
    """
    Book a hotel reservation using POST method to AWS API Gateway
    """
    
    logger.info("🎫 ADK FUNCTION TOOL: hotel_booking called")
    logger.info(f"📋 Booking hotel offer: {hotelOfferId} for {primary_guest_firstName} {primary_guest_lastName}")
    
    # Validate required parameters
    if not hotelOfferId:
        return {
            "status": "error",
            "message": "Hotel offer ID is required for booking",
            "booking_confirmed": False
        }
    
    # Build the complete booking payload
    booking_payload = {
        "data": {
            "type": "hotel-order",
            "guests": [
                {
                    "tid": 1,
                    "title": primary_guest_title.upper(),
                    "firstName": primary_guest_firstName.upper(),
                    "lastName": primary_guest_lastName.upper(),
                    "phone": primary_guest_phone,
                    "email": primary_guest_email
                }
            ],
            "travelAgent": {
                "contact": {
                    "email": travel_agent_email or primary_guest_email
                }
            },
            "roomAssociations": [
                {
                    "guestReferences": [
                        {"guestReference": "1"}
                    ],
                    "hotelOfferId": hotelOfferId
                }
            ],
            "payment": {
                "method": "CREDIT_CARD",
                "paymentCard": {
                    "paymentCardInfo": {
                        "vendorCode": payment_vendorCode,
                        "cardNumber": payment_cardNumber,
                        "expiryDate": payment_expiryDate,
                        "holderName": payment_holderName.upper()
                    }
                }
            }
        }
    }
    
    # Use booking tool if available
    if AWS_TOOLS_AVAILABLE and HOTEL_BOOKING_TOOL:
        logger.info("🔧 Using HotelBookingTool for reservation")
        
        try:
            # The tool will handle POST method internally
            primary_guest = {
                "title": primary_guest_title,
                "firstName": primary_guest_firstName,
                "lastName": primary_guest_lastName,
                "email": primary_guest_email,
                "phone": primary_guest_phone
            }
            
            payment_info = {
                "vendorCode": payment_vendorCode,
                "cardNumber": payment_cardNumber,
                "expiryDate": payment_expiryDate,
                "holderName": payment_holderName
            }
            
            result = await HOTEL_BOOKING_TOOL.execute(
                hotelOfferId=hotelOfferId,
                primary_guest=primary_guest,
                payment_info=payment_info,
                travel_agent_email=travel_agent_email or primary_guest_email
            )
            
            logger.info(f"✅ Booking result: {result.get('status')}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Booking tool failed: {e}")
    
    # Fallback: Direct POST API call
    logger.info("🔄 Using direct POST API call for booking")
    
    api_url = f"{AWS_BASE_URL}/booking/hotel-orders-v2"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': AWS_API_KEY
    }
    
    try:
        logger.info(f"📤 Making POST request to: {api_url}")
        logger.info(f"📋 Payload: {json.dumps(booking_payload, indent=2)}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # ✅ CORRECT: Using POST method for booking
            response = await client.post(api_url, json=booking_payload, headers=headers)
            
            logger.info(f"📨 Booking API Response: {response.status_code}")
            
            if response.status_code in [200, 201, 202]:  # Accept multiple success codes
                booking_data = response.json()
                
                # Extract confirmation details
                confirmation_data = booking_data.get("data", booking_data)
                confirmation_number = confirmation_data.get("id", confirmation_data.get("confirmationId", "BOOKING_CONFIRMED"))
                
                return {
                    "status": "success",
                    "booking_confirmed": True,
                    "confirmation_number": confirmation_number,
                    "booking_details": {
                        "hotel_offer_id": hotelOfferId,
                        "primary_guest": f"{primary_guest_firstName} {primary_guest_lastName}",
                        "guest_email": primary_guest_email,
                        "payment_method": f"{payment_vendorCode} ending in {payment_cardNumber[-4:]}",
                        "booking_reference": confirmation_data.get("bookingReference", confirmation_number)
                    },
                    "api_response": booking_data,
                    "source": "Direct_POST_API_Gateway"
                }
            else:
                logger.error(f"❌ Booking API error: {response.status_code} - {response.text}")
                return {
                    "status": "booking_failed",
                    "booking_confirmed": False,
                    "error_message": f"Booking API returned {response.status_code}: {response.text}",
                    "hotel_offer_id": hotelOfferId
                }
                
    except httpx.TimeoutException:
        logger.error("⏰ Booking API request timeout")
        return {
            "status": "timeout",
            "booking_confirmed": False,
            "message": "Booking request timed out. Please try again.",
            "hotel_offer_id": hotelOfferId
        }
    except Exception as e:
        logger.error(f"❌ Direct booking POST request failed: {e}")
        return {
            "status": "error",
            "booking_confirmed": False,
            "message": f"Booking failed: {str(e)}",
            "hotel_offer_id": hotelOfferId
        }
        
async def hotel_search(hotelIds: str, 
                     adults: int,
                     checkInDate: str, 
                     checkOutDate: str,) -> Dict[str, Any]:
    """
    Main hotel search function with AWS API Gateway integration and A2A compatibility
    """
    
    logger.info("🏨 ADK FUNCTION TOOL: hotel_geocode_search called")
    
    if not checkInDate or checkInDate.strip() == "":
        return {
            "status": "error",
            "error_message": "Check-in date is required in YYYY-MM-DD format.",
            "hotels": []
        }
    
    # Auto-calculate check-out date if empty
    if not checkOutDate or checkOutDate.strip() == "":
        try:
            check_in_date = datetime.strptime(checkInDate, "%Y-%m-%d")
            check_out_date = check_in_date + timedelta(days=3)
            checkOutDate = check_out_date.strftime("%Y-%m-%d")
            logger.info(f"🗓️ Auto-calculated check-out date: {checkOutDate}")
        except ValueError:
            return {
                "status": "error",
                "error_message": f"Invalid check-in date format: {checkInDate}. Use YYYY-MM-DD.",
                "hotels": []
            }
    
    # Try existing AWS tool first
    logger.info("🔧 Using existing HotelSearchTool")
    
    try:
        result = await _make_direct_api_call_search(
            hotelIds, checkInDate, checkOutDate, adults
        )
        
        logger.info(f"Result: {result}")
        
        logger.info(f"✅ HotelSearchTool executed successfully")
        
        offers = result.get("offers", [])
        
        logger.info(offers)
        
        # Apply trip-type prioritization
        # if hotels and tripType:
        #     if tripType == "romantic":
        #         hotels = _prioritize_romantic_hotels(hotels)
        #     elif tripType == "business":
        #         hotels = _prioritize_business_hotels(hotels)
        #     elif tripType == "family":
        #         hotels = _prioritize_family_hotels(hotels)
        
        # Generate price summary
        
        return {
            "status": result.get("status", "success"),
            "offers": offers,  # Limit to top 10
            "total_results": len(offers),
            "search_criteria": {
                "hotelIds": hotelIds,
                "adults": adults,
                "checkInDate": checkInDate,
                "checkOutDate": checkOutDate,
            },
            "api_gateway_triggered": True,
            "tool_used": "existing_HotelSearchTool",
            "source": "AWS_API_Gateway_Amadeus_GDS"
        }
        
    except Exception as e:
        logger.error(f"❌ HotelSearchTool execution failed: {e}")
        
        result = await _make_direct_api_call_search(
            hotelIds, adults, checkInDate, checkOutDate
        )

async def hotel_geocode_search(cityCode: str, latitude: float, longitude: float,
                      checkIn: str, checkOut: str, adults: int, 
                      children: int, radius: int, radiusUnit: str,
                      chainCodes: str, amenities: str, ratings: str,
                      hotelSource: str, pageLimit: int, pageOffset: int,
                      tripType: str) -> Dict[str, Any]:
    """
    Main hotel search function with AWS API Gateway integration and A2A compatibility
    """
    
    logger.info("🏨 ADK FUNCTION TOOL: hotel_geocode_search called")
    logger.info(f"📍 Parameters: {cityCode}, {checkIn} to {checkOut}, {adults} adults, {children} children")
    
    # Handle "default" logic inside the function
    if not cityCode or len(cityCode) != 3:
        return {
            "status": "error",
            "error_message": f"Invalid city code: {cityCode}. Must be 3 letters (e.g., PAR, LON, NYC).",
            "hotels": []
        }
    
    if not checkIn or checkIn.strip() == "":
        return {
            "status": "error",
            "error_message": "Check-in date is required in YYYY-MM-DD format.",
            "hotels": []
        }
    
    # Auto-calculate check-out date if empty
    if not checkOut or checkOut.strip() == "":
        try:
            check_in_date = datetime.strptime(checkIn, "%Y-%m-%d")
            check_out_date = check_in_date + timedelta(days=3)
            checkOut = check_out_date.strftime("%Y-%m-%d")
            logger.info(f"🗓️ Auto-calculated check-out date: {checkOut}")
        except ValueError:
            return {
                "status": "error",
                "error_message": f"Invalid check-in date format: {checkIn}. Use YYYY-MM-DD.",
                "hotels": []
            }
    
    # Handle zero coordinates
    if latitude == 0.0 and longitude == 0.0:
        try:
            city_info = location_db.get_city_info(cityCode)
            latitude = city_info["latitude"]
            longitude = city_info["longitude"]
            logger.info(f"📍 Resolved coordinates for {cityCode}: ({latitude}, {longitude})")
        except Exception as e:
            logger.error(f"❌ Coordinate resolution failed: {e}")
            latitude, longitude = 48.8566, 2.3522  # Default to Paris
    
    # Handle empty strings and defaults
    if not radiusUnit or radiusUnit.strip() == "":
        radiusUnit = "KM"
    
    if (radius or 0) <= 0:
        radius = 5

    
    if (adults or 0) <= 0:
        adults = 2
        
    if (children or 0) < 0:
        children = 0
    
    if not hotelSource or hotelSource.strip() == "":
        hotelSource = "ALL"
        
    if (pageLimit or 0) <= 0:
        pageLimit = 99
        
    if (pageOffset or 0) < 0:
        pageOffset = 0
    
    if not tripType or tripType.strip() == "":
        tripType = "leisure"
    
    # Map trip type to amenities if not specified
    if not amenities or amenities.strip() == "":
        if tripType == "business":
            amenities = "BUSINESS_CENTER,WIFI,MEETING_ROOM"
        elif tripType == "romantic":
            amenities = "SPA,RESTAURANT"
        elif tripType == "family":
            amenities = "POOL,KIDS_CLUB,FAMILY_ROOM"
        else:
            amenities = ""
    
    # Try existing AWS tool first
    if AWS_TOOLS_AVAILABLE and HOTEL_GEOCODE_SEARCH_TOOL:
        logger.info("🔧 Using existing HotelSearchTool")
        
        try:
            result = await HOTEL_GEOCODE_SEARCH_TOOL.execute(
                cityCode=cityCode.upper(),
                latitude=latitude,
                longitude=longitude,
                radius=radius,
                radiusUnit=radiusUnit,
                adults=adults,
                children=children,
                chainCodes=chainCodes or "",
                amenities=amenities,
                ratings=ratings or "",
                hotelSource=hotelSource,
                checkIn=checkIn,
                checkOut=checkOut,
                pageLimit=pageLimit,
                pageOffset=pageOffset
            )
            
            logger.info(f"✅ HotelSearchTool executed successfully")
            
            hotels = result.get("hotels", [])
            
            logger.info(hotels)
            
            # Apply trip-type prioritization
            # if hotels and tripType:
            #     if tripType == "romantic":
            #         hotels = _prioritize_romantic_hotels(hotels)
            #     elif tripType == "business":
            #         hotels = _prioritize_business_hotels(hotels)
            #     elif tripType == "family":
            #         hotels = _prioritize_family_hotels(hotels)
            
            # Generate price summary
            
            return {
                "status": result.get("status", "success"),
                "hotels": hotels[:10],  # Limit to top 10
                "total_results": len(hotels),
                "search_criteria": {
                    "cityCode": cityCode.upper(),
                    "checkIn": checkIn,
                    "checkOut": checkOut,
                    "adults": adults,
                    "children": children,
                    "tripType": tripType
                },
                "api_gateway_triggered": True,
                "tool_used": "existing_HotelGeocodeSearchTool",
                "source": "AWS_API_Gateway_Amadeus_GDS"
            }
            
        except Exception as e:
            logger.error(f"❌ HotelSearchTool execution failed: {e}")
    
    # Fallback: Direct API call
    logger.info("🔄 Using direct API Gateway call")
    result = await _make_direct_api_call(
        cityCode, latitude, longitude, checkIn, checkOut, adults, children,
        radius, radiusUnit, chainCodes or "", amenities, ratings or "", 
        hotelSource, pageLimit, pageOffset
    )
    
    if result["status"] == "success" and result["hotels"]:
        # Apply trip-type prioritization
        hotels = result["hotels"]
        if tripType:
            if tripType == "romantic":
                hotels = _prioritize_romantic_hotels(hotels)
            elif tripType == "business":
                hotels = _prioritize_business_hotels(hotels)
            elif tripType == "family":
                hotels = _prioritize_family_hotels(hotels)
        
        # Generate price summary
        
        result["hotels"] = hotels[:10]
        result["search_criteria"] = {
            "cityCode": cityCode.upper(),
            "checkIn": checkIn,
            "checkOut": checkOut,
            "adults": adults,
            "children": children,
            "tripType": tripType
        }
        return result
    
    # Final fallback: Mock data
    logger.info("🔄 Using mock data fallback")
    mock_result = await _get_mock_hotels(cityCode, checkIn, checkOut, adults, children, tripType)
    return mock_result

# === SIMPLIFIED ADK AGENT CREATION ===

def create_hotel_specialist_agent():
    """Create Hotel Specialist Agent with Google AI compatible instructions"""
    
    logger.info("🏨 Creating Hotel Specialist Agent with no default parameters")
    
    agent = LlmAgent(
        name="hotel_specialist_agent",
        model="gemini-2.0-flash",
        tools=[hotel_geocode_search, hotel_search, hotel_booking],
        instruction="""You are an Expert Hotel Specialist, powered by a live Amadeus GDS connection through AWS. Your primary goal is to help users find and book hotels seamlessly.

        **CRITICAL WORKFLOW:**
        1.  **SEARCH FIRST FOR THE HOTEL NAME AND ID USING GEOCODE:** For any hotel request, you MUST use the `hotel_geocode_search` tool first. You need a city, check-in date, and number of adults. After listing of hotels, recommend the user the hotelId "RTPAR001" 
        2.  **SEARCH OFFERS USING THE USER'S DESIRED HOTEL ID FROM THE HOTEL LIST:** When the user provided the hotelId along with the check in date, check out date, and the adults, trigger the `hotel_search` tool. 
        3.  **GUIDE TO BOOK:** After presenting offers results, ask the user if they want to book one by providing its `hotelOfferId`.
   
        ---
        **HOTEL BOOKING PROCESS (Follow these steps precisely):**

        **STEP 1: INITIATE HOTEL NAME AND HOTEL ID SEARCH**
        PHASE A:
        The user will provide its intent of hotel name and hotel id.
        
        PHASE B:
        Hotel id from Phase A will be used as hotelIds as part of payload to look for offers.id that can be extracted from response array.
        
        PHASE C:
        The user will signal their intent to book by providing a `hotelOfferId` from the offers result of Phase B.
        
        TAKE NOTE: 
        PHASE A AND PHASE B WILL REQUIRE COMMON PARAMETERS (checkInDate, checkOutDate, adults) THE CORE DIFFERENCE IS PHASE B USES `hotelIds` WITH `s` TO AVOID CONFUSION.
        Use YYYY-MM-DD format for checkInDate and checkOutDate

        **STEP 2: GATHER GUEST INFORMATION**
        Once the user provides a `hotelOfferId`, you MUST collect the following information for **EACH GUEST**. If they say "2 guests", you must ask for two sets of details.
        - Title (e.g., MR, MS, MRS)
        - First Name
        - Last Name
        - Phone Number (including country code)
        - Email Address

        **Example dialogue:** "Great! To book Hotel ID [hotelOfferId], I'll need the details for all [number] guests. Let's start with the first guest: What is their title, first name, last name, phone, and email?"

        **STEP 3: CRITICAL PAYMENT INSTRUCTION (DO NOT DEVIATE)**
        **DO NOT ASK THE USER FOR CREDIT CARD INFORMATION.** The system is configured for a test environment and requires a static, hardcoded credit card to process the booking. You must use these exact details when calling the `hotel_booking` function. This is non-negotiable.

        **STEP 4: EXECUTE BOOKING**
        Once you have collected all required guest details for the specified number of guests, call the `hotel_booking` function. The payload you construct must include:
        - The `hotelOfferId` provided by the user.
        - A list of guest objects, one for each guest whose details you collected.

        **STEP 5: CONFIRM SUCCESS**
        After the `hotel_booking` function returns a successful response, you MUST inform the user and provide their booking ID.
        - Look for `"bookingStatus": "CONFIRMED"` in the response.
        - Extract the booking ID from `data.hotelBookings[0].id`.
        - Present the confirmation clearly to the user.

        **Confirmation Message Example:** "Excellent! Your booking is confirmed. Your official booking ID is [id]. You will receive a confirmation email shortly. Is there anything else I can assist you with?"

        ---
        A2A Message Note:
        Your response should be complete and and sent back to the trip_orchestrator_agent. 
        
        **FORBIDDEN ACTIONS:**
        - NEVER ask for credit card details.
        - NEVER attempt to book without a valid `hotelOfferId` from a prior search.
        - NEVER invent a booking ID. Only provide the one from the successful API response.
        """,
        description="Hotel specialist that handles search and uses a precise, rule-based process for booking with static payment details."
    )
    
    logger.info("✅ Hotel Specialist Agent created with fixed parameters")
    return agent


# Create agent instances
hotel_specialist_agent = create_hotel_specialist_agent()
agent = hotel_specialist_agent
root_agent = hotel_specialist_agent

# === A2A FASTAPI APPLICATION (SIMPLIFIED) ===

app = FastAPI(
    title="Hotel Specialist Agent - A2A Enabled (Simplified)",
    version="1.2.0",
    description="Simplified A2A-enabled hotel specialist with AWS API Gateway integration"
)

# Create alias for uvicorn
a2a_app = app

# === A2A ENDPOINTS (SIMPLIFIED) ===

@app.post("/chat") 
async def a2a_chat_endpoint(message_data: A2AMessage):
    """A2A Main chat endpoint"""
    try:
        logger.info(f"🔗 A2A chat request received: {message_data.message}")
        
        # Create ADK session for agent interaction
        session_service = InMemorySessionService()
        runner = Runner(
            agent=hotel_specialist_agent, 
            app_name="hotel_a2a_app", 
            session_service=session_service
        )
        
        session_id = message_data.session_id or f"a2a_session_{uuid.uuid4()}"
        user_id = message_data.user_id or "a2a_user"
        
        # Create session
        await session_service.create_session(
            app_name="hotel_a2a_app", 
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
            agent_id="hotel_specialist_agent",
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
            response=f"I encountered an error processing your hotel request: {str(e)}. Please try again.",
            status="error",
            agent_id="hotel_specialist_agent",
            metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
        )

@app.get("/health")
async def health_check():
    """A2A Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "hotel_specialist_agent",
        "version": "1.2.0",
        "a2a_enabled": True,
        "aws_tools_available": AWS_TOOLS_AVAILABLE,
        "simplified_mode": True,
        "timestamp": datetime.now().isoformat()
    }

# === SERVER MANAGEMENT ===

async def start_a2a_server():
    """Start the simplified A2A-enabled hotel specialist server"""
    
    print("🚀 Starting Simplified Hotel Specialist Agent with A2A Protocol")
    print("=" * 70)
    print(f"🔗 A2A Agent Card: http://localhost:8004/.well-known/agent_card")
    print(f"💬 A2A Chat Endpoint: http://localhost:8004/chat") 
    print(f"❤️ Health Check: http://localhost:8004/health")
    print(f"🔧 AWS Tools Available: {AWS_TOOLS_AVAILABLE}")
    print(f"✨ Simplified Mode: No separate price analysis function")
    print("=" * 70)
    
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=8004,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

async def test_hotel_geocode_search():
    """Test simplified hotel search"""
    print("🧪 Testing Simplified Hotel Search")
    
    result = await hotel_geocode_search(
        cityCode="PAR",
        checkIn="2025-07-10",
        checkOut="2025-07-13",
        adults=2,
        tripType="romantic"
    )
    
    print(f"✅ Hotel search: {result['status']}")
    print(f"🏨 Found: {len(result.get('hotels', []))} hotels")

# === MAIN EXECUTION ===

async def main():
    """Main execution function"""
    
    print("🏨 Simplified Hotel Specialist Agent - A2A Enabled")
    print("Choose execution mode:")
    print("1. Start A2A Server")
    print("2. Test Hotel Search Function")
    
    try:
        mode = input("Enter choice (1-2): ").strip()
    except:
        mode = "1"
    
    if mode == "1":
        await start_a2a_server()
    elif mode == "2":
        await test_hotel_geocode_search()
    else:
        await start_a2a_server()

# === ENSURE ALL EXPORTS ARE AVAILABLE ===

print(f"🔧 Debug: hotel_specialist_agent exists: {hotel_specialist_agent is not None}")
print(f"🔧 Debug: agent exists: {agent is not None}")
print(f"🔧 Debug: app/a2a_app exists: {app is not None}")
print(f"🔧 Debug: location_db exists: {location_db is not None}")
print(f"🔧 Debug: AWS_TOOLS_AVAILABLE: {AWS_TOOLS_AVAILABLE}")

if __name__ == "__main__":
    asyncio.run(main())
