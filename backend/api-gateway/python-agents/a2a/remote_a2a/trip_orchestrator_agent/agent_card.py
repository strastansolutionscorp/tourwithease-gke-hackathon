from datetime import datetime
from typing import Dict, Any
import yaml
from pathlib import Path

from .. schemas.agent_card import AgentCard, ToolSchema, ToolParameter, AgentEndpoint

def load_agent_config() -> Dict[str, Any]:
    config_path = Path(__file__).parent / "agent_config.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

config = load_agent_config()

# Updated Tool Schemas with Intelligent Routing
TOOL_SCHEMAS = [
    ToolSchema(
        name="intelligent_agent_routing",
        description="Intelligently analyze user messages and automatically route to the most appropriate specialist agent",
        parameters=[
            ToolParameter(name="user_message", type="string", description="User's travel-related message", required=True),
            ToolParameter(name="context", type="object", description="Optional additional context", required=False)
        ],
        returns={
            "type": "object", 
            "description": "Response from the selected specialist agent with routing metadata",
            "properties": {
                "routing_metadata": {"type": "object", "description": "Information about agent selection and routing decision"},
                "specialist_response": {"type": "object", "description": "Response from the selected specialist agent"},
                "status": {"type": "string", "description": "Routing operation status"}
            }
        }
    ),
    ToolSchema(
        name="plan_trip_from_request",
        description="Comprehensive trip planning with automatic specialist coordination",
        parameters=[
            ToolParameter(name="user_request", type="string", description="Natural language trip request", required=True),
            ToolParameter(name="context", type="object", description="Additional context", required=False)
        ],
        returns={
            "type": "object", 
            "description": "Structured trip plan with coordination results from specialist agents",
            "properties": {
                "trip_analysis": {"type": "object", "description": "Parsed trip requirements"},
                "specialist_results": {"type": "object", "description": "Results from coordinated specialist agents"},
                "coordination_status": {"type": "string", "description": "Status of agent coordination"}
            }
        }
    ),
    ToolSchema(
        name="analyze_trip_prices",
        description="Analyze and compare prices across different travel components",
        parameters=[
            ToolParameter(name="options", type="array", description="List of travel options to analyze", required=True),
            ToolParameter(name="criteria", type="object", description="Analysis criteria", required=False)
        ],
        returns={
            "type": "object",
            "description": "Comprehensive price analysis with recommendations"
        }
    ),
    ToolSchema(
        name="coordinate_travel_booking",
        description="Coordinate travel bookings across multiple services",
        parameters=[
            ToolParameter(name="booking_type", type="string", description="Type of booking (flight, hotel, package)", required=True),
            ToolParameter(name="booking_details", type="object", description="Booking details", required=True),
            ToolParameter(name="passenger_info", type="object", description="Passenger information", required=True)
        ],
        returns={
            "type": "object",
            "description": "Booking coordination results with confirmation details"
        }
    ),
    ToolSchema(
        name="get_trip_recommendations",
        description="Get comprehensive trip recommendations based on destination and preferences",
        parameters=[
            ToolParameter(name="destination", type="string", description="Travel destination", required=True),
            ToolParameter(name="trip_type", type="string", description="Type of trip", required=False, default="leisure"),
            ToolParameter(name="budget", type="number", description="Total budget", required=False),
            ToolParameter(name="duration", type="integer", description="Trip duration in days", required=False)
        ],
        returns={
            "type": "string",
            "description": "Comprehensive trip recommendations as formatted text"
        }
    )
]

# Enhanced Agent Card with Intelligent Routing Focus
TRIP_ORCHESTRATOR_AGENT_CARD = AgentCard(
    name=config["name"],

    version=config["version"],
    description="Intelligent travel orchestrator with automatic specialist agent routing - analyzes user queries and seamlessly delegates to the most appropriate specialist agent for optimal responses",
    author=config["metadata"]["author"],
    created_date=datetime.now().isoformat(),
    
    # Enhanced capabilities with intelligent routing as primary feature
    capabilities=[
        "intelligent_agent_routing",      # NEW - Primary capability
        "automatic_query_analysis",       # NEW - Message analysis for routing
        "seamless_specialist_delegation", # NEW - Transparent routing to specialists
        "multi_agent_coordination",       # Enhanced - Coordinate multiple specialists
        "cross_domain_optimization",      # Enhanced - Optimize across all travel domains
        "comprehensive_trip_planning",    # Enhanced - Through intelligent routing
        "price_analysis",                 # Enhanced - Across all components
        "travel_recommendations",         # Enhanced - Synthesized from specialists
        "booking_coordination",           # Enhanced - Coordinate complex bookings
        "context_aware_responses"         # NEW - Maintain context across agent calls
    ],
    
    tools=TOOL_SCHEMAS,
    
    endpoints=[
        AgentEndpoint(path="/chat", method="POST", description="Main intelligent routing endpoint"),
        AgentEndpoint(path="/health", method="GET", description="Health check"),
        AgentEndpoint(path="/.well-known/agent_card", method="GET", description="Agent card metadata"),
        AgentEndpoint(path="/capabilities", method="GET", description="Agent capabilities and routing info"),
        # Enhanced routing-specific endpoints
        AgentEndpoint(path="/routing-analytics", method="GET", description="Routing decision analytics"),
        AgentEndpoint(path="/specialist-status", method="GET", description="Check all specialist agent availability")
    ],
    
    communication_protocols=["HTTP", "A2A"],
    base_url=f"http://localhost:{config['port']}",
    health_check_endpoint="/health",
    authentication={"type": "none", "required": False},
    
    # Enhanced metadata with intelligent routing details
    metadata={
        **config["metadata"],
        
        # Core routing intelligence metadata
        "agent_type": "intelligent_orchestrator",
        "routing_method": "automatic_analysis",
        "primary_function": "intelligent_specialist_routing",
        
        # Routing intelligence features
        "routing_intelligence": {
            "analysis_method": "keyword_and_pattern_matching",
            "confidence_scoring": True,
            "fallback_strategies": True,
            "context_awareness": True,
            "learning_capability": False  # Could be enhanced later
        },
        
        # Specialist agents this orchestrator routes to
        "routes_to_specialists": [
            {
                "agent_name": "flight_specialist_agent",
                "agent_url": "http://localhost:8003",
                "specialties": ["flights", "airlines", "aviation", "flight booking"],
                "routing_keywords": ["flight", "fly", "plane", "airline", "airport", "ticket", "departure", "arrival"],
                "priority_score": 0.9
            },
            {
                "agent_name": "hotel_specialist_agent", 
                "agent_url": "http://localhost:8005",
                "specialties": ["hotels", "accommodation", "lodging", "hospitality"],
                "routing_keywords": ["hotel", "accommodation", "stay", "room", "lodge", "resort", "check-in", "booking"],
                "priority_score": 0.9
            },
            {
                "agent_name": "context_specialist_agent",
                "agent_url": "http://localhost:8004", 
                "specialties": ["destination info", "weather", "culture", "currency", "travel context"],
                "routing_keywords": ["weather", "culture", "currency", "language", "customs", "visa", "climate", "local", "destination"],
                "priority_score": 0.8
            }
        ],
        
        # Routing decision patterns
        "routing_patterns": {
            "keyword_matching": {
                "enabled": True,
                "weight": 0.6,
                "description": "Match user message keywords to specialist domains"
            },
            "pattern_analysis": {
                "enabled": True,
                "weight": 0.3,
                "description": "Analyze message patterns (questions, actions, comparisons)"
            },
            "context_consideration": {
                "enabled": True,
                "weight": 0.1,
                "description": "Consider conversation context and history"
            }
        },
        
        # Performance characteristics for intelligent routing
        "routing_performance": {
            "analysis_time": "< 100ms",
            "routing_accuracy": "~90%",
            "fallback_success_rate": "~95%",
            "concurrent_routing_support": True,
            "max_routing_attempts": 3
        },
        
        # Routing decision transparency
        "transparency_features": {
            "routing_explanation": True,
            "confidence_scoring": True,
            "alternative_agent_suggestions": True,
            "routing_history_tracking": True
        },
        
        # Advanced routing capabilities
        "advanced_routing_features": [
            "multi_keyword_analysis",        # Analyze multiple relevant keywords
            "intent_recognition",            # Recognize user intent (book, ask, compare)
            "domain_expertise_matching",     # Match query complexity to agent expertise
            "context_carry_forward",         # Maintain context across agent calls
            "intelligent_fallback",          # Smart fallback when primary agent unavailable
            "routing_optimization"           # Optimize routing decisions over time
        ],
        
        # Integration patterns
        "integration_patterns": {
            "transparent_routing": "User sees seamless responses without knowing about routing",
            "specialist_coordination": "Can coordinate multiple specialists for complex queries", 
            "context_preservation": "Maintains conversation context across specialist calls",
            "response_synthesis": "Combines specialist responses into coherent answers"
        },
        
        # Quality assurance for routing
        "routing_quality_assurance": {
            "confidence_thresholds": {
                "high_confidence": 0.8,
                "medium_confidence": 0.5,
                "low_confidence": 0.3
            },
            "fallback_strategies": [
                "Default to context specialist for general queries",
                "Use multiple specialists for complex queries",
                "Provide routing explanation when confidence is low"
            ],
            "error_handling": [
                "Graceful degradation when specialists unavailable",
                "Retry logic with exponential backoff",
                "Clear error messages with alternative suggestions"
            ]
        },
        
        # Monitoring and analytics
        "routing_analytics": {
            "tracks_routing_decisions": True,
            "measures_routing_accuracy": True,
            "monitors_specialist_performance": True,
            "provides_routing_insights": True,
            "supports_routing_optimization": True
        }
    }
)

def get_agent_card() -> AgentCard:
    return TRIP_ORCHESTRATOR_AGENT_CARD

def get_specialist_routing_config() -> Dict[str, Dict[str, Any]]:
    """Get routing configuration for specialist agents"""
    return {
        agent["agent_name"]: {
            "url": agent["agent_url"],
            "specialties": agent["specialties"],
            "keywords": agent["routing_keywords"],
            "priority": agent["priority_score"]
        }
        for agent in TRIP_ORCHESTRATOR_AGENT_CARD.metadata["routes_to_specialists"]
    }

def get_routing_patterns() -> Dict[str, Any]:
    """Get routing decision patterns and weights"""
    return TRIP_ORCHESTRATOR_AGENT_CARD.metadata["routing_patterns"]

def get_routing_performance_metrics() -> Dict[str, Any]:
    """Get routing performance characteristics"""
    return TRIP_ORCHESTRATOR_AGENT_CARD.metadata["routing_performance"]
