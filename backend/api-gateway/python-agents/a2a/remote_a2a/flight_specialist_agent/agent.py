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
from fastapi.responses import JSONResponse

# Import agent card
from .agent_card import get_agent_card

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

# AWS Lambda Tools for Flight Operations
async def search_flights_aws(
    origin: str,
    destination: str, 
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1,
    cabin_class: str = "ECONOMY",
    trip_type: str = "leisure",
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Search for flights using AWS Lambda via API Gateway
    
    Args:
        origin: Departure city or airport code
        destination: Arrival city or airport code  
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (optional)
        passengers: Number of passengers
        cabin_class: Cabin class (ECONOMY, BUSINESS, FIRST)
        trip_type: Type of trip (leisure, business, romantic)
        tool_context: Tool context for state management
    
    Returns:
        Dictionary containing flight search results
    """
    payload = {
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "passengers": passengers,
        "cabin_class": cabin_class,
        "trip_type": trip_type
    }
    
    try:
        # Get AWS credentials from environment
        api_key = os.getenv('AWS_API_KEY')
        base_url = os.getenv('AWS_API_GATEWAY_URL')
        
        if not api_key or not base_url:
            # Return mock data if AWS not configured
            return await _get_mock_flight_data(payload, trip_type)
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
        
        url = f"{base_url}/search"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            flights = result.get("flights", [])
            
            # Apply trip-type prioritization
            if trip_type == "romantic":
                flights = _prioritize_romantic_flights(flights)
            elif trip_type == "business":
                flights = _prioritize_business_flights(flights)
            
            # Store in context if available
            if tool_context and 'flight_searches' not in tool_context.state:
                tool_context.state['flight_searches'] = []
            if tool_context:
                tool_context.state['flight_searches'].append({
                    'search_params': payload,
                    'results_count': len(flights),
                    'timestamp': datetime.now().isoformat()
                })
            
            return {
                "status": "success",
                "flights": flights,
                "search_criteria": payload,
                "total_found": len(flights)
            }
            
    except httpx.HTTPError as e:
        logging.error(f"HTTP error in flight search: {e}")
        return await _get_mock_flight_data(payload, trip_type)
    except Exception as e:
        logging.error(f"Flight search error: {e}")
        return {
            "status": "error",
            "message": f"Flight search failed: {str(e)}",
            "search_criteria": payload
        }

async def analyze_flight_prices(
    flights: List[Dict[str, Any]], 
    criteria: Optional[Dict[str, Any]] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """Analyze flight prices and provide insights
    
    Args:
        flights: List of flight options to analyze
        criteria: Analysis criteria (optional)
        tool_context: Tool context for state management
    
    Returns:
        Dictionary containing price analysis results
    """
    if not flights:
        return {"status": "no_data", "message": "No flights to analyze"}

    # Extract prices from flights
    prices = []
    for flight in flights:
        price = flight.get("price")
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
    min_price_idx = next(i for i, flight in enumerate(flights) 
                        if flight.get("price") == min(prices))
    analysis["recommendations"].append({
        "type": "best_value",
        "flight_index": min_price_idx,
        "reason": "Lowest price option",
        "savings": max(prices) - min(prices)
    })

    # Find middle-priced option
    sorted_with_indices = sorted(enumerate(flights), 
                               key=lambda x: float(x[1].get("price", float('inf'))))
    if len(sorted_with_indices) > 1:
        mid_idx = sorted_with_indices[len(sorted_with_indices)//2][0]
        analysis["recommendations"].append({
            "type": "balanced",
            "flight_index": mid_idx,
            "reason": "Good balance of price and quality"
        })

    # Store analysis in context
    if tool_context:
        if 'price_analyses' not in tool_context.state:
            tool_context.state['price_analyses'] = []
        tool_context.state['price_analyses'].append({
            'analysis_result': analysis,
            'flights_analyzed': len(flights),
            'timestamp': datetime.now().isoformat()
        })

    return analysis

async def get_flight_recommendations(
    origin: str,
    destination: str,
    trip_type: str = "leisure",
    budget: Optional[float] = None,
    tool_context: ToolContext = None
) -> str:
    """Get personalized flight recommendations
    
    Args:
        origin: Departure location
        destination: Destination location  
        trip_type: Type of trip
        budget: Optional budget constraint
        tool_context: Tool context for state management
        
    Returns:
        Personalized recommendations as string
    """
    recommendations = []
    
    if trip_type == "romantic":
        recommendations.extend([
            f"For romantic trips to {destination}, consider evening departure flights",
            "Premium airlines like Emirates or Qatar Airways offer better ambiance",
            "Business class upgrades can make the journey more special"
        ])
    elif trip_type == "business":
        recommendations.extend([
            f"For business travel to {destination}, morning flights (8-10 AM) are optimal",
            "Choose airlines with good business lounges and Wi-Fi",
            "Direct flights save time and reduce fatigue"
        ])
    else:
        recommendations.extend([
            f"For leisure travel to {destination}, mid-week flights often cost less",
            "Compare prices across different airlines",
            "Consider connecting flights to save money"
        ])
    
    if budget:
        recommendations.append(f"With a budget of ${budget}, focus on economy class and off-peak times")
    
    # Store recommendations in context
    if tool_context:
        if 'recommendations' not in tool_context.state:
            tool_context.state['recommendations'] = []
        tool_context.state['recommendations'].append({
            'origin': origin,
            'destination': destination,
            'trip_type': trip_type,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        })
    
    return "Flight Recommendations:\n" + "\n".join(f"• {rec}" for rec in recommendations)

# Helper functions
async def _get_mock_flight_data(payload: Dict[str, Any], trip_type: str) -> Dict[str, Any]:
    """Generate mock flight data when AWS is not available"""
    origin = payload.get("origin", "NYC")
    destination = payload.get("destination", "PAR")
    departure_date = payload.get("departure_date", "2024-03-15")
    
    flights = [
        {
            "id": f"FL{i:03d}",
            "airline": ["Delta Air Lines", "American Airlines", "United Airlines", "Air France"][i],
            "origin": origin,
            "destination": destination,  
            "departure_time": f"{departure_date} {8+i*3:02d}:00",
            "arrival_time": f"{departure_date} {16+i*3:02d}:30",
            "duration_minutes": 480 + i*30,
            "price": 450 + i*150,
            "currency": "USD",
            "cabin_class": payload.get("cabin_class", "ECONOMY"),
            "stops": 0 if i < 2 else 1,
            "aircraft_type": "Boeing 777" if i % 2 == 0 else "Airbus A350"
        } for i in range(4)
    ]
    
    # Apply prioritization based on trip type
    if trip_type == "romantic":
        flights = _prioritize_romantic_flights(flights)
    elif trip_type == "business":
        flights = _prioritize_business_flights(flights)
    
    return {
        "status": "success",
        "flights": flights,
        "search_criteria": payload,
        "total_found": len(flights),
        "note": "Mock data - AWS Lambda not configured"
    }

def _prioritize_romantic_flights(flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize flights suitable for romantic trips"""
    def romantic_score(flight):
        score = 0
        departure_time = flight.get("departure_time", "")
        
        # Extract hour from departure time
        try:
            hour = int(departure_time.split()[-1].split(":")[0])
            if 18 <= hour <= 20:  # Evening flights
                score += 3
        except (ValueError, IndexError):
            pass
            
        if flight.get("airline") in ["Emirates", "Qatar Airways", "Singapore Airlines", "Air France"]:
            score += 2  # Premium airlines
        if flight.get("cabin_class") in ["BUSINESS", "FIRST"]:
            score += 1  # Premium cabins
        if flight.get("stops", 1) == 0:  # Direct flights
            score += 1
            
        flight["romantic_score"] = score
        return score
    
    return sorted(flights, key=romantic_score, reverse=True)

def _prioritize_business_flights(flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize flights suitable for business trips"""  
    def business_score(flight):
        score = 0
        departure_time = flight.get("departure_time", "")
        
        # Extract hour from departure time
        try:
            hour = int(departure_time.split()[-1].split(":")[0])
            if 8 <= hour <= 10:  # Morning flights
                score += 3
            elif 13 <= hour <= 15:  # Early afternoon
                score += 2
        except (ValueError, IndexError):
            pass
            
        if flight.get("airline") in ["American Airlines", "Delta", "United", "Lufthansa"]:
            score += 2  # Business-friendly airlines
        if flight.get("cabin_class") == "BUSINESS":
            score += 1
        if flight.get("duration_minutes", 999) < 480:  # Under 8 hours
            score += 1
        if flight.get("stops", 1) == 0:  # Direct flights
            score += 1
            
        flight["business_score"] = score
        return score
    
    return sorted(flights, key=business_score, reverse=True)

# Create safety settings from config
safety_settings = []
for setting in config.get("safety_settings", []):
    safety_settings.append(
        types.SafetySetting(
            category=getattr(types.HarmCategory, setting["category"]),
            threshold=getattr(types.HarmBlockThreshold, setting["threshold"]),
        )
    )
    
# Create the Flight Specialist Agent
flight_specialist_agent = Agent(
    model=config["model"],
    name=config["name"],
    description=config["description"],
    instruction=config["instruction"],
    tools=[
        search_flights_aws,
        analyze_flight_prices,
        get_flight_recommendations,
    ],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=safety_settings,
        temperature=config["model_config"]["temperature"],
        top_p=config["model_config"]["top_p"],
        max_output_tokens=config["model_config"]["max_output_tokens"],
    ),
)

# Convert to A2A application
a2a_app = to_a2a(flight_specialist_agent, port=config["port"])

# Add agent card endpoint
@a2a_app.get("/.well-known/agent_card")
async def get_agent_card_endpoint():
    agent_card = get_agent_card()
    return JSONResponse(content=agent_card.dict())

@a2a_app.get("/capabilities")
async def get_capabilities():
    agent_card = get_agent_card()
    return {
        "agent": config["name"],
        "capabilities": agent_card.capabilities,
        "tools": [tool.name for tool in agent_card.tools],
        "aws_integration": config["metadata"]["aws_integration"]
    }
