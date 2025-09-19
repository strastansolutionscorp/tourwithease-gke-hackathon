# api/main.py
from fastapi import FastAPI, WebSocket, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os
from agents.trip_orchestrator import TripOrchestrator
from messaging.a2a_bus import A2AMessageBus
from agents.flight_specialist import FlightSpecialist
from agents.hotel_specialist import HotelSpecialist
from agents.context_specialist import ContextSpecialist

from agents.trip_orchestrator_agent.agent import TripOrchestrator
from agents.flight_specialist_agent.agent import FlightSpecialist  
from agents.hotel_specialist_agent.agent import HotelSpecialist

CLIENT_ID = "261080872553-a0rad105bg3q2eg6om421o94dad3a44b.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://127.0.0.1:8000/dev-ui/"
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="TourWithEase ADK API",
    description="Multi-Agent Travel Planning API with ADK and A2A Protocol",
    version="1.0.0"
)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"
    user_context: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    status: str
    message: str
    conversation_id: str
    results: Optional[Dict[str, Any]] = None
    next_actions: Optional[list] = None
    timestamp: str

class AgentStatus(BaseModel):
    agent_name: str
    status: str
    last_activity: str


# Global variables
message_bus: A2AMessageBus = None
orchestrator: TripOrchestrator = None
agents: Dict[str, Any] = {}
active_connections: Dict[str, WebSocket] = {}

@app.get("/login")
def login():
    return RedirectResponse(
        f"{AUTH_URI}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=openid%20email%20profile"
    )
    
@app.get("/dev-ui/")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if code:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TOKEN_URI,
                data={
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code"
                }
            )
            tokens = response.json()
            # Store tokens in session or pass to agent
            return tokens
    return {"error": "No code provided"}

@app.on_event("startup")
async def startup_event():
    """Initialize agents and message bus on startup"""
    global message_bus, orchestrator, agents
    logger.info("Initializing ADK agents and A2A message bus...")

    # Initialize message bus
    redis_url = os.getenv("REDIS_URL", "redis://redis-service:6379")
    message_bus = A2AMessageBus(redis_url)
    await message_bus.initialize()

    # Initialize agents
    orchestrator = TripOrchestrator()
    flight_agent = FlightSpecialist()
    hotel_agent = HotelSpecialist()
    context_agent = ContextSpecialist()

    agents = {
        "trip-orchestrator": orchestrator,
        "flight-specialist": flight_agent,
        "hotel-specialist": hotel_agent,
        "context-specialist": context_agent
    }

    # Initialize all agents
    for agent_name, agent in agents.items():
        await agent.initialize()
        await message_bus.register_agent(agent)

    logger.info(f"Initialized agent: {agent_name}")
    # Start message bus listener
    listen_task = await message_bus.start_listening()
    logger.info("A2A message bus started")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token - simplified for hackathon"""
    # In production, implement proper JWT verification
    return {"user_id": "demo_user", "permissions": ["chat"]}

@app.get("/")
    async def root():
    """Health check endpoint"""
    return {
        "service": "TourWithEase ADK API",
        "status": "running",
        "agents": list(agents.keys()),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/agents/status")
    async def get_agents_status():
        """Get status of all agents"""
        agent_statuses = []
        for agent_name, agent in agents.items():
        agent_statuses.append(AgentStatus(
        agent_name=agent_name,
        status=agent.status.value,
        last_activity=datetime.utcnow().isoformat()
    ))

    return agent_statuses


@app.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(
        request: ChatRequest,
        background_tasks: BackgroundTasks,
        user: dict = Depends(verify_token)
    ):
        """Main chat endpoint for travel planning"""
        try:
            logger.info(f"Processing chat request: {request.message[:50]}...")
            # Process request through orchestrator
            result = await orchestrator.process_request({
            "message": request.message,
            "conversation_id": request.conversation_id,
            "user_context": request.user_context,
            "user_id": user["user_id"]
        })
    response = ChatResponse(
        status=result.get("status", "success"),
        message=result.get("message", "I'm here to help with your travel planning!"),
        conversation_id=request.conversation_id,
        results=result.get("results"),
        next_actions=result.get("next_actions"),
        timestamp=datetime.utcnow().isoformat()
    )

        # Send real-time update via WebSocket if connected
        if request.conversation_id in active_connections:
            background_tasks.add_task(
            send_websocket_update,
            request.conversation_id,
            response.dict()
        )
        return response

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{conversation_id}")
    async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time updates"""
        await websocket.accept()
        active_connections[conversation_id] = websocket
    try:
        logger.info(f"WebSocket connected: {conversation_id}")
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to TourWithEase AI",
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep connection alive
        while True:
            try:
                # Wait for ping/pong messages
                data = await websocket.receive_text()
                ping_data = json.loads(data)
                if ping_data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if conversation_id in active_connections:
        del active_connections[conversation_id]
        logger.info(f"WebSocket disconnected: {conversation_id}")

    async def send_websocket_update(conversation_id: str, data: dict):
    """Send update via WebSocket"""
        if conversation_id in active_connections:

            try:
                websocket = active_connections[conversation_id]
                await websocket.send_json({
                    "type": "chat_response",
                    "data": data
                })

            except Exception as e:
                logger.error(f"Failed to send WebSocket update: {e}")


@app.get("/conversation/{conversation_id}/history")
    async def get_conversation_history(
        conversation_id: str,
        user: dict = Depends(verify_token)
    ):
        """Get conversation history"""
        if orchestrator and orchestrator.memory:
            history = orchestrator.memory.get_conversation_context()
            return {
                "conversation_id": conversation_id,
                "history": history,
                "total_messages": len(history)
            }
        else:
            return {
                "conversation_id": conversation_id,
                "history": [],
                "total_messages": 0
            }

@app.post("/agents/{agent_name}/direct")
    async def direct_agent_request(
        agent_name: str,
        request: Dict[str, Any],
        user: dict = Depends(verify_token)
    ):
    """Send direct request to specific agent (for testing/debugging)"""
        if agent_name not in agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} not found")
        try:
            agent = agents[agent_name]
            result = await agent.process_request(request)
        return {
            "agent": agent_name,
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/metrics")
    async def get_metrics():
        """Get system metrics"""
        return {
            "active_connections": len(active_connections),
            "agents_count": len(agents),
            "uptime": "running", # Simplified for hackathon
            "message_bus_status": "connected" if message_bus else "disconnected"
        }
    if __name__ == "__main__":
    import uvicorn
        Kubernetes Deployment Manifests
        Namespace and ConfigMap
        Redis Deployment for A2A Message Bus
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            log_level="info"
        )

async def main():
    """Main application entry point"""
    
    # Initialize the A2A message bus
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    message_bus = A2AMessageBus(redis_url)
    await message_bus.initialize()
    
    # Create agents
    trip_orchestrator = TripOrchestrator()
    flight_specialist = FlightSpecialist()
    hotel_specialist = HotelSpecialist()
    
    # Set message bus for each agent
    trip_orchestrator.set_message_bus(message_bus)
    flight_specialist.set_message_bus(message_bus)
    hotel_specialist.set_message_bus(message_bus)
    
    # Initialize agents (this registers them with the message bus)
    await trip_orchestrator.initialize()
    await flight_specialist.initialize()
    await hotel_specialist.initialize()
    
    # Start message bus listening
    listen_task = await message_bus.start_listening()
    
    print("🚀 All agents are running and connected!")
    print("You can now send requests to the trip-orchestrator")
    
    # Example: Send a test request to the orchestrator
    test_request = {
        "message": "I want to plan a romantic trip to Paris next week",
        "conversation_id": "test-conversation-1"
    }
    
    print(f"\n📤 Sending test request: {test_request['message']}")
    response = await trip_orchestrator.process_request(test_request)
    print(f"📥 Response: {response}")
    
    # Keep running until interrupted
    try:
        await listen_task
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        await message_bus.stop_listening()

if __name__ == "__main__":
    asyncio.run(main())