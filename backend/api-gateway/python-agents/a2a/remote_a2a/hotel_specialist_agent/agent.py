# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

import asyncio
import os
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import yaml
from pathlib import Path
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from fastapi.responses import JSONResponse  # ✅ FIXED: Use FastAPI instead of Starlette

# Load environment variables
load_dotenv()

# Load configuration
def load_config():
    config_path = Path(__file__).parent / "agent_config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_config()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hotel Search Tools for A2A Integration
async def search_hotels_aws(
    city_code: str,
    check_in: str,
    check_out: str = None,
    guests: int = 1,
    rooms: int = 1,
    hotel_type: Optional[str] = None,
    trip_type: str = "leisure",
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Search for hotels using AWS Lambda via API Gateway
    
    Args:
        city_code: Destination city code or name
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        rooms: Number of rooms
        hotel_type: Type of hotel (luxury, business, family)
        trip_type: Type of trip (leisure, business, romantic, family)
        tool_context: Tool context for state management
        
    Returns:
        Dictionary containing hotel search results
    """
    logger.info(f"Searching hotels in {city_code} for {guests} guests")
    
    # Auto-calculate check_out if not provided
    if check_in and not check_out:
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = check_in_date + timedelta(days=3)
            check_out = check_out_date.strftime("%Y-%m-%d")
            logger.info(f"Auto-calculated check-out date: {check_out}")
        except ValueError:
            logger.error(f"Invalid check-in date format: {check_in}")
            return {
                "status": "error",
                "message": "Invalid check-in date format. Use YYYY-MM-DD.",
                "search_criteria": {"city_code": city_code, "check_in": check_in}
            }

    # Determine hotel type based on trip type if not specified
    if not hotel_type:
        if trip_type == "romantic":
            hotel_type = "luxury"
        elif trip_type == "business":
            hotel_type = "business"
        elif trip_type == "family":
            hotel_type = "family"

    payload = {
        "city_code": city_code,
        "check_in": check_in,
        "check_out": check_out,
        "guests": guests,
        "rooms": rooms,
        "hotel_type": hotel_type,
        "trip_type": trip_type
    }

    try:
        # Get AWS credentials
        api_key = os.getenv('AWS_API_KEY')
        base_url = os.getenv('AWS_API_GATEWAY_URL')
        
        if not api_key or not base_url:
            # Return mock data if AWS not configured
            return await _get_mock_hotel_data(payload, trip_type)

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
        
        url = f"{base_url}/hotel-search"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            hotels = result.get("hotels", [])
            
            # Apply trip-type prioritization
            if trip_type == "romantic":
                hotels = _prioritize_romantic_hotels(hotels)
            elif trip_type == "business":
                hotels = _prioritize_business_hotels(hotels)
            elif trip_type == "family":
                hotels = _prioritize_family_hotels(hotels)
            
            # Store in context
            if tool_context:
                if 'hotel_searches' not in tool_context.state:
                    tool_context.state['hotel_searches'] = []
                tool_context.state['hotel_searches'].append({
                    'search_params': payload,
                    'results_count': len(hotels),
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                "status": "success",
                "hotels": hotels,
                "search_criteria": payload,
                "total_found": len(hotels),
                "recommendations": _generate_hotel_recommendations(hotels, trip_type)
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error in hotel search: {e}")
        return await _get_mock_hotel_data(payload, trip_type)
    except Exception as e:
        logger.error(f"Hotel search error: {e}")
        return {
            "status": "error",
            "message": f"Hotel search failed: {str(e)}",
            "search_criteria": payload
        }

async def analyze_hotel_prices(
    hotels: List[Dict[str, Any]], 
    criteria: Optional[Dict[str, Any]] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Analyze hotel prices and provide insights
    
    Args:
        hotels: List of hotel options to analyze
        criteria: Analysis criteria (optional)
        tool_context: Tool context for state management
        
    Returns:
        Dictionary containing price analysis results
    """
    if not hotels:
        return {"status": "no_data", "message": "No hotels to analyze"}

    # Extract prices from hotels
    prices = []
    for hotel in hotels:
        price = hotel.get("price_per_night") or hotel.get("price")
        if price is not None:
            try:
                prices.append(float(price))
            except (ValueError, TypeError):
                continue

    if not prices:
        return {"status": "no_prices", "message": "No valid price data available"}

    # Perform price analysis
    analysis = {
        "status": "success",
        "price_range": {
            "min": min(prices),
            "max": max(prices),
            "average": sum(prices) / len(prices),
            "median": sorted(prices)[len(prices)//2]
        },
        "recommendations": []
    }

    # Add recommendations based on price analysis
    min_price_idx = next(i for i, hotel in enumerate(hotels) 
                        if float(hotel.get("price_per_night", hotel.get("price", 0))) == min(prices))
    analysis["recommendations"].append({
        "type": "best_value",
        "hotel_index": min_price_idx,
        "reason": "Lowest price option",
        "savings": max(prices) - min(prices)
    })

    # Find middle-priced option
    sorted_with_indices = sorted(enumerate(hotels), 
                               key=lambda x: float(x[1].get("price_per_night", x[1].get("price", float('inf')))))
    if len(sorted_with_indices) > 1:
        mid_idx = sorted_with_indices[len(sorted_with_indices)//2][0]
        analysis["recommendations"].append({
            "type": "balanced",
            "hotel_index": mid_idx,
            "reason": "Good balance of price and amenities"
        })

    # Store analysis in context
    if tool_context:
        if 'price_analyses' not in tool_context.state:
            tool_context.state['price_analyses'] = []
        tool_context.state['price_analyses'].append({
            'analysis_result': analysis,
            'hotels_analyzed': len(hotels),
            'timestamp': datetime.now().isoformat()
        })

    return analysis

async def get_hotel_recommendations(
    destination: str,
    trip_type: str = "leisure",
    budget: Optional[float] = None,
    special_needs: Optional[str] = None,
    tool_context: ToolContext = None
) -> str:
    """Get personalized hotel recommendations
    
    Args:
        destination: Destination city
        trip_type: Type of trip
        budget: Optional budget per night
        special_needs: Special requirements (accessibility, pet-friendly, etc.)
        tool_context: Tool context for state management
        
    Returns:
        Personalized recommendations as string
    """
    recommendations = []
    
    if trip_type == "romantic":
        recommendations.extend([
            f"For romantic stays in {destination}, look for boutique hotels or luxury properties",
            "Hotels with spa services, rooftop bars, or scenic views are ideal",
            "Consider properties with in-room amenities like jacuzzis or balconies",
            "Central locations near romantic dining and attractions are preferred"
        ])
    elif trip_type == "business":
        recommendations.extend([
            f"For business travel to {destination}, prioritize hotels near business districts",
            "Look for properties with business centers, meeting rooms, and reliable WiFi",
            "Airport proximity and express check-in/out services are valuable",
            "Hotel brands with loyalty programs often provide better business amenities"
        ])
    elif trip_type == "family":
        recommendations.extend([
            f"For family trips to {destination}, choose hotels with family-friendly amenities",
            "Look for properties with pools, kids' clubs, and connecting rooms",
            "Hotels near family attractions and with complimentary breakfast save money",
            "Safety features and childproofing are important considerations"
        ])
    else:
        recommendations.extend([
            f"For leisure travel to {destination}, balance location with value",
            "Consider hotels near public transport for easy city exploration",
            "Read recent reviews for service quality and cleanliness standards",
            "Book directly with hotels for potential upgrades and flexible policies"
        ])
    
    if budget:
        recommendations.append(f"With a budget of ${budget}/night, focus on mid-range properties with good reviews")
    
    if special_needs:
        recommendations.append(f"For {special_needs}, contact hotels directly to confirm specific accommodations")
    
    # Store recommendations in context
    if tool_context:
        if 'recommendations' not in tool_context.state:
            tool_context.state['recommendations'] = []
        tool_context.state['recommendations'].append({
            'destination': destination,
            'trip_type': trip_type,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
    
    return "Hotel Recommendations:\n" + "\n".join(f"• {rec}" for rec in recommendations)

# Helper functions (you'll need to add these - they were truncated in your code)
async def _get_mock_hotel_data(payload: Dict[str, Any], trip_type: str) -> Dict[str, Any]:
    """Generate mock hotel data when AWS is not available"""
    destination = payload.get("city_code", "PAR")
    check_in = payload.get("check_in", "2024-03-15")
    
    hotels = [
        {
            "id": f"HTL{i:03d}",
            "name": f"Hotel {destination} {['Grand', 'Royal', 'Plaza', 'Boutique'][i]}",
            "location": destination,
            "category": 3 + i,  # 3-6 star rating
            "price_per_night": 120 + i*60,
            "currency": "USD",
            "amenities": _get_amenities_for_trip_type(trip_type, i),
            "distance_to_center": f"{1 + i*0.8}km",
            "rating": 3.8 + i*0.3,
            "availability": True,
            "description": f"{'Luxury' if i >= 2 else 'Comfortable'} hotel in {destination}"
        } for i in range(4)
    ]
    
    return {
        "status": "success",
        "hotels": hotels,
        "search_criteria": payload,
        "total_found": len(hotels),
        "note": "Mock data - AWS Lambda not configured",
        "recommendations": _generate_hotel_recommendations(hotels, trip_type)
    }

def _get_amenities_for_trip_type(trip_type: str, hotel_level: int) -> List[str]:
    """Get amenities based on trip type and hotel level"""
    base_amenities = ["WiFi", "24h Reception", "Concierge"]
    
    if trip_type == "romantic":
        return base_amenities + ["Spa", "Fine Dining", "Room Service", "Couples Massage", "Rooftop Bar"][:(2+hotel_level)]
    elif trip_type == "business":
        return base_amenities + ["Business Center", "Conference Rooms", "Express Check-in", "Airport Shuttle"][:(2+hotel_level)]
    elif trip_type == "family":
        return base_amenities + ["Pool", "Kids Club", "Family Rooms", "Playground", "Babysitting"][:(2+hotel_level)]
    else:
        return base_amenities + ["Pool", "Restaurant", "Fitness Center", "Laundry"][:(2+hotel_level)]

def _prioritize_romantic_hotels(hotels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize hotels for romantic trips"""
    for hotel in hotels:
        score = 0
        if hotel.get("category", 0) >= 4:
            score += 3
        amenities = hotel.get("amenities", [])
        if any("spa" in amenity.lower() for amenity in amenities):
            score += 2
        hotel["romantic_score"] = score
    
    return sorted(hotels, key=lambda x: (-x.get("romantic_score", 0), float(x.get("price_per_night", 999999))))

def _prioritize_business_hotels(hotels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize hotels for business travel"""
    for hotel in hotels:
        score = 0
        amenities = hotel.get("amenities", [])
        if any("business" in amenity.lower() for amenity in amenities):
            score += 3
        hotel["business_score"] = score
    
    return sorted(hotels, key=lambda x: (-x.get("business_score", 0), float(x.get("price_per_night", 999999))))

def _prioritize_family_hotels(hotels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize hotels for family travel"""
    for hotel in hotels:
        score = 0
        amenities = hotel.get("amenities", [])
        if any("pool" in amenity.lower() or "kids" in amenity.lower() for amenity in amenities):
            score += 3
        hotel["family_score"] = score
    
    return sorted(hotels, key=lambda x: (-x.get("family_score", 0), float(x.get("price_per_night", 999999))))

def _generate_hotel_recommendations(hotels: List[Dict[str, Any]], trip_type: str) -> List[Dict[str, Any]]:
    """Generate recommendations based on hotel analysis"""
    if not hotels:
        return []
    
    recommendations = []
    if len(hotels) > 0:
        recommendations.append({
            "type": "best_value",
            "hotel_index": 0,
            "title": f"Perfect for your {trip_type} trip",
            "reason": f"This hotel offers the best combination of amenities and location for {trip_type} travelers."
        })

    return recommendations

# Create safety settings from config
safety_settings = []
for setting in config.get("safety_settings", []):
    safety_settings.append(
        types.SafetySetting(
            category=getattr(types.HarmCategory, setting["category"]),
            threshold=getattr(types.HarmBlockThreshold, setting["threshold"]),
        )
    )

# Create the Hotel Specialist Agent
hotel_specialist_agent = Agent(
    model=config["model"],
    name=config["name"],
    description=config["description"],
    instruction=config["instruction"],
    tools=[
        search_hotels_aws,
        analyze_hotel_prices,
        get_hotel_recommendations,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=safety_settings,
        temperature=config["model_config"]["temperature"],
        top_p=config["model_config"]["top_p"],
        max_output_tokens=config["model_config"]["max_output_tokens"],
    ),
)

# Convert to A2A application
a2a_app = to_a2a(hotel_specialist_agent, port=config["port"])

# Add endpoints
@a2a_app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": config["name"]}

@a2a_app.get("/capabilities")
async def get_capabilities():
    return {
        "agent": config["name"],
        "tools": ["search_hotels_aws", "analyze_hotel_prices", "get_hotel_recommendations"],
        "aws_integration": True
    }
