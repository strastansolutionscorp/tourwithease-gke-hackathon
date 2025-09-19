# flight_specialist_agent/agent_card.py
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
        name="search_flights_aws",
        description="Search for flights using AWS Lambda and Amadeus GDS",
        parameters=[
            ToolParameter(name="origin", type="string", description="Departure airport/city", required=True),
            ToolParameter(name="destination", type="string", description="Arrival airport/city", required=True),
            ToolParameter(name="departure_date", type="string", description="Departure date (YYYY-MM-DD)", required=True),
            ToolParameter(name="return_date", type="string", description="Return date (optional)", required=False),
            ToolParameter(name="passengers", type="integer", description="Number of passengers", required=False, default=1),
            ToolParameter(name="cabin_class", type="string", description="Cabin class", required=False, enum=["ECONOMY", "BUSINESS", "FIRST"]),
            ToolParameter(name="trip_type", type="string", description="Trip type", required=False, enum=["leisure", "business", "romantic"])
        ],
        returns={"type": "object", "description": "Flight search results with pricing and details"}
    ),
    ToolSchema(
        name="analyze_flight_prices",
        description="Analyze flight prices and provide insights",
        parameters=[
            ToolParameter(name="flights", type="array", description="List of flight options to analyze", required=True),
            ToolParameter(name="criteria", type="object", description="Analysis criteria", required=False)
        ],
        returns={"type": "object", "description": "Price analysis with recommendations"}
    ),
    ToolSchema(
        name="get_flight_recommendations",
        description="Get personalized flight recommendations",
        parameters=[
            ToolParameter(name="origin", type="string", description="Departure location", required=True),
            ToolParameter(name="destination", type="string", description="Destination location", required=True),
            ToolParameter(name="trip_type", type="string", description="Type of trip", required=False, enum=["leisure", "business", "romantic"]),
            ToolParameter(name="budget", type="number", description="Budget constraint", required=False)
        ],
        returns={"type": "string", "description": "Personalized recommendations"}
    )
]

FLIGHT_SPECIALIST_AGENT_CARD = AgentCard(
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
    return FLIGHT_SPECIALIST_AGENT_CARD
