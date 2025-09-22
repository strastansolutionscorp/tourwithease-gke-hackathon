"""
Trip Orchestrator Agent - Intelligent multi-specialist coordination
"""

__version__ = "2.1.0"

# Main exports
from .agent import (
    trip_orchestrator_agent,
    root_agent,
    intelligent_agent_routing_with_session,
    SPECIALIST_AGENTS,
    config,
    app
)

# Make the orchestrator easily accessible
__all__ = [
    "trip_orchestrator_agent",
    "root_agent", 
    "intelligent_agent_routing_with_session",
    "SPECIALIST_AGENTS",
    "config",
    "app"
]

# Orchestrator info
ORCHESTRATOR_INFO = {
    "name": "trip_orchestrator_agent",
    "version": __version__,
    "description": "Intelligent travel orchestrator with multi-agent coordination",
    "port": 8001,
    "specialists": ["context_specialist", "flight_specialist", "hotel_specialist"]
}

# Quick health check function
async def quick_health_check():
    """Quick health check for orchestrator system"""
    try:
        from .agent import _check_agent_availability
        
        specialist_status = {}
        for name, info in SPECIALIST_AGENTS.items():
            specialist_status[name] = await _check_agent_availability(info["url"])
        
        return {
            "orchestrator": "healthy",
            "specialists": specialist_status,
            "total_available": sum(specialist_status.values())
        }
    except Exception as e:
        return {"error": str(e)}
