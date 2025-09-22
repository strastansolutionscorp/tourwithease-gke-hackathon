# === a2a_implementation.py ===
"""
A2A Protocol implementation for Hotel Specialist Agent
Separate file to avoid circular imports
"""

import asyncio
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
import uvicorn

# Import components from agent (only what we need)
try:
    from .agent import agent, hotel_search, location_db
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    agent = None
    hotel_search = None
    location_db = None

logger = logging.getLogger(__name__)

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

# === AGENT CARD ===

FLIGHT_SPECIALIST_AGENT_CARD = {
    "name": "flight_specialist_agent",
    "version": "1.2.0",
    "description": "Expert flight specialist with AWS API Gateway integration for real-time flight search, pricing analysis, and booking using Amadeus GDS data",
    "protocol_version": "1.0",
    "author": "TourWithEase",
    
    # A2A Protocol compliance
    "agent_type": "specialist",
    "communication_protocols": ["HTTP", "A2A", "JSON-RPC"],
    
    # Service endpoints
    "base_url": "http://localhost:8003",  # Flight specialist port
    "endpoints": [
        {
            "path": "/chat",
            "method": "POST",
            "description": "Main A2A chat endpoint for flight specialist communication",
            "input_format": "A2AMessage",
            "output_format": "A2AResponse"
        },
        {
            "path": "/health",
            "method": "GET", 
            "description": "Health check endpoint"
        },
        {
            "path": "/.well-known/agent_card",
            "method": "GET",
            "description": "Agent card metadata for A2A discovery"
        },
        {
            "path": "/flight/search",
            "method": "POST", 
            "description": "Direct flight search endpoint"
        }
    ],
    
    # Capabilities
    "capabilities": [
        "flight_search",
        "price_analysis",
        "flight_booking",
        "aws_lambda_integration",
        "amadeus_gds_access",
        "real_time_availability"
    ],
    
    # Service discovery keywords
    "service_discovery": {
        "keywords": ["flight", "airline", "booking", "travel", "airplane", "airport"],
        "categories": ["travel", "transportation", "booking"],
        "priority": 0.9
    },
    
    "metadata": {
        "model": "gemini-2.0-flash",
        "framework": "google_adk",
        "port": 8003,
        "specializations": [
            "flight_search_optimization",
            "price_analysis",
            "route_optimization",
            "aws_api_gateway_integration",
            "amadeus_gds_connectivity"
        ]
    }
}

# === FASTAPI APP ===

app = FastAPI(
    title="Flight Specialist Agent - A2A",
    version="1.2.0",
    description="A2A-enabled flight specialist"
)

@app.get("/.well-known/agent_card")
async def get_agent_card():
    """Agent card for A2A discovery"""
    return JSONResponse(content=FLIGHT_SPECIALIST_AGENT_CARD)

@app.post("/chat")
async def a2a_chat_endpoint(message_data: A2AMessage):
    """A2A chat endpoint"""
    try:
        if not AGENT_AVAILABLE:
            return A2AResponse(
                response="Flight specialist agent is not available. Please check the configuration.",
                status="error",
                metadata={"error": "agent_not_available"}
            )
        
        # Simple response for now - you can enhance this
        response_text = f"Flight specialist received: {message_data.message}"
        
        return A2AResponse(
            response=response_text,
            status="success",
            session_id=message_data.session_id or f"session_{uuid.uuid4()}",
            metadata={"timestamp": datetime.now().isoformat()}
        )
        
    except Exception as e:
        return A2AResponse(
            response=f"Error processing request: {str(e)}",
            status="error",
            metadata={"error": str(e)}
        )
        
@app.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities for A2A discovery"""
    return {
        "agent": "flight_specialist_agent",
        "capabilities": FLIGHT_SPECIALIST_AGENT_CARD["capabilities"],
        "tools": ["flight_search", "flight_price_analysis"],
        "specializations": FLIGHT_SPECIALIST_AGENT_CARD["metadata"]["specializations"],
        "integration_status": {
            "amadeus_gds": True
        },
        "a2a_protocol": "1.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "flight_specialist_agent",
        "a2a_enabled": True,
        "agent_available": AGENT_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# === A2A CLIENT ===

class A2AFlightClient:
    """A2A client for testing"""
    
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url
    
    async def send_chat_message(self, message: str, context: dict = None):
        """Send A2A chat message"""
        payload = A2AMessage(
            message=message,
            context=context or {}
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat",
                json=payload.dict()
            )
            return response.json()

# === SERVER FUNCTIONS ===

async def start_a2a_server():
    """Start A2A server"""
    print("🚀 Starting Flight Specialist A2A Server")
    print(f"🔗 Agent Card: http://localhost:8003/.well-known/agent_card")
    print(f"💬 Chat Endpoint: http://localhost:8003/chat")
    print(f"❤️ Health Check: http://localhost:8003/health")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8003, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

# async def test_a2a_integration():
#     """Test A2A integration"""
#     print("🧪 Testing A2A Integration")
    
#     client = A2AHotelClient()
    
#     try:
#         response = await client.send_chat_message(
#             "Find hotels in Paris for July 10-13, 2025"
#         )
#         print(f"✅ A2A Test Response: {response}")
        
#     except Exception as e:
#         print(f"❌ A2A Test Failed: {e}")
