# context_specialist_agent/agent_card.py
from datetime import datetime
from typing import Dict, Any
import yaml
from pathlib import Path

# Import schemas
from ...schemas.agent_card import AgentCard, ToolSchema, ToolParameter, AgentEndpoint

# Load configuration
def load_agent_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent / "agent_config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Load config
config = load_agent_config()

# Define tool schemas
TOOL_SCHEMAS = [
    ToolSchema(
        name="get_weather_info",
        description="Get weather information and travel recommendations",
        parameters=[
            ToolParameter(name="location", type="string", description="Destination location", required=True),
            ToolParameter(name="date", type="string", description="Travel date (YYYY-MM-DD)", required=False)
        ],
        returns={"type": "object", "description": "Weather forecast and travel advice"}
    ),
    ToolSchema(
        name="get_currency_info", 
        description="Get currency and payment information",
        parameters=[
            ToolParameter(name="destination", type="string", description="Destination country/city", required=True)
        ],
        returns={"type": "object", "description": "Currency details and payment methods"}
    ),
    ToolSchema(
        name="get_cultural_insights",
        description="Get cultural insights and etiquette tips",
        parameters=[
            ToolParameter(name="destination", type="string", description="Destination location", required=True),
            ToolParameter(name="trip_type", type="string", description="Type of trip", required=False, enum=["leisure", "business", "romantic", "family"])
        ],
        returns={"type": "string", "description": "Cultural guide and etiquette tips"}
    ),
    ToolSchema(
        name="get_comprehensive_travel_context",
        description="Get complete travel context with weather, currency, and cultural information",
        parameters=[
            ToolParameter(name="destination", type="string", description="Travel destination", required=True),
            ToolParameter(name="trip_type", type="string", description="Type of trip", required=False, enum=["leisure", "business", "romantic", "family"]),
            ToolParameter(name="travel_date", type="string", description="Travel date (YYYY-MM-DD)", required=False)
        ],
        returns={"type": "string", "description": "Comprehensive travel context summary"}
    )
]

# Create Agent Card
CONTEXT_SPECIALIST_AGENT_CARD = AgentCard(
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
    """Get the agent card for this agent"""
    return CONTEXT_SPECIALIST_AGENT_CARD
