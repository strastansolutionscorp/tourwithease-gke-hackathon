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
    agent_id: str = "hotel_specialist_agent"
    session_id: Optional[str] = None
    metadata: Optional[dict] = {}

# === AGENT CARD ===

HOTEL_SPECIALIST_AGENT_CARD = {
    "name": "hotel_specialist_agent",
    "version": "1.2.0",
    "description": "Expert hotel specialist with AWS API Gateway integration",
    "protocol_version": "1.0",
    "author": "TourWithEase",
    "agent_type": "specialist",
    "communication_protocols": ["HTTP", "A2A", "JSON-RPC"],
    "base_url": "http://localhost:8004",
    "endpoints": [
        {"path": "/chat", "method": "POST", "description": "A2A chat endpoint", "input_format": "A2AMessage", "output_format": "A2AResponse"},
        {"path": "/health", "method": "GET", "description": "Health check"},
        {"path": "/.well-known/agent_card", "method": "GET", "description": "Agent discovery"}
    ],
    "capabilities": [
        "hotel_search",
        "accommodation_analysis",
        "price_comparison"
    ],
    "keywords": ["hotel", "accommodation", "stay", "room", "booking"]
}

# === FASTAPI APP ===

app = FastAPI(
    title="Hotel Specialist Agent - A2A",
    version="1.2.0",
    description="A2A-enabled hotel specialist"
)

@app.get("/.well-known/agent_card")
async def get_agent_card():
    """Agent card for A2A discovery"""
    return JSONResponse(content=HOTEL_SPECIALIST_AGENT_CARD)

@app.post("/chat")
async def a2a_chat_endpoint(message_data: A2AMessage):
    """A2A chat endpoint"""
    try:
        if not AGENT_AVAILABLE:
            return A2AResponse(
                response="Hotel specialist agent is not available. Please check the configuration.",
                status="error",
                metadata={"error": "agent_not_available"}
            )
        
        # Simple response for now - you can enhance this
        response_text = f"Hotel specialist received: {message_data.message}"
        
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "hotel_specialist_agent",
        "a2a_enabled": True,
        "agent_available": AGENT_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

# === A2A CLIENT ===

class A2AHotelClient:
    """A2A client for testing"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
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
    print("🚀 Starting Hotel Specialist A2A Server")
    print(f"🔗 Agent Card: http://localhost:8004/.well-known/agent_card")
    print(f"💬 Chat Endpoint: http://localhost:8004/chat")
    print(f"❤️ Health Check: http://localhost:8004/health")
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8004, log_level="info")
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
