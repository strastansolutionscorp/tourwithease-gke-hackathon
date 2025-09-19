# hotel_specialist_agent/agent_card.py
from datetime import datetime
from typing import Dict, Any
import yaml
from pathlib import Path

from ...schemas.agent_card import AgentCard, ToolSchema, ToolParameter, AgentEndpoint

def load_agent_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent / "agent_config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_agent_config()

TOOL_SCHEMAS = [
    ToolSchema(
        name="search_hotels_aws",
        description="Search for hotels using AWS Lambda and Amadeus GDS",
        parameters=[
            ToolParameter(name="city_code", type="string", description="Destination city code/name", required=True),
            ToolParameter(name="check_in", type="string", description="Check-in date (YYYY-MM-DD)", required=True),
            ToolParameter(name="check_out", type="string", description="Check-out date (YYYY-MM-DD)", required=False),
            ToolParameter(name="guests", type="integer", description="Number of guests", required=False, default=1),
            ToolParameter(name="rooms", type="integer", description="Number of rooms", required=False, default=1),
            ToolParameter(name="hotel_type", type="string", description="Hotel type preference", required=False, enum=["luxury", "business", "family", "budget"]),
            ToolParameter(name="trip_type", type="string", description="Trip type", required=False, enum=["leisure", "business", "romantic", "family"])
        ],
        returns={"type": "object", "description": "Hotel search results with pricing and amenities"}
    ),
    ToolSchema(
        name="analyze_hotel_prices",
        description="Analyze hotel prices and provide insights",
        parameters=[
            ToolParameter(name="hotels", type="array", description="List of hotel options to analyze", required=True),
            ToolParameter(name="criteria", type="object", description="Analysis criteria", required=False)
        ],
        returns={"type": "object", "description": "Price analysis with recommendations"}
    ),
    ToolSchema(
        name="get_hotel_recommendations",
        description="Get personalized hotel recommendations",
        parameters=[
            ToolParameter(name="destination", type="string", description="Destination city", required=True),
            ToolParameter(name="trip_type", type="string", description="Type of trip", required=False, enum=["leisure", "business", "romantic", "family"]),
            ToolParameter(name="budget", type="number", description="Budget per night", required=False),
            ToolParameter(name="special_needs", type="string", description="Special requirements", required=False)
        ],
        returns={"type": "string", "description": "Personalized hotel recommendations"}
    )
]

HOTEL_SPECIALIST_AGENT_CARD = AgentCard(
    name=config["name"],
    version=config["version"],
    description=config["description"],
    author=config["metadata"]["author"],
    created_date=datetime.now().isoformat(),
    capabilities=config["capabilities"],
    tools=TOOL_SCHEMAS,
    endpoints=[
        AgentEndpoint(path="/chat", method="POST", description="Main chat endpoint"),
        AgentEndpoint(path="/health", method="GET", description="Health check"),
        AgentEndpoint(path="/.well-known/agent_card", method="GET", description="Agent card metadata")
    ],
    communication_protocols=["HTTP", "A2A"],
    base_url=f"http://localhost:{config['port']}",
    health_check_endpoint="/health",
    authentication={"type": "none", "required": False},
    metadata=config["metadata"]
)

def get_agent_card() -> AgentCard:
    return HOTEL_SPECIALIST_AGENT_CARD
