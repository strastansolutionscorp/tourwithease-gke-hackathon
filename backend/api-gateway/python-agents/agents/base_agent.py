from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio
import json
import logging
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    OFFLINE = "offline"

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    HEARTBEAT = "heartbeat"


@dataclass
class A2AMessage:
    """A2A Protocol Message Format"""
    id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    conversation_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "correlation_id": self.correlation_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        return cls(
            id=data["id"],
            from_agent=data["from_agent"],
            to_agent=data["to_agent"],
            message_type=MessageType(data["message_type"]),
            payload=data["payload"],
            conversation_id=data.get("conversation_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None,
            correlation_id=data.get("correlation_id")
        )


class Tool(ABC):
    """Abstract base class for agent tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        pass


class Memory:
    """Agent memory management"""
    
    def __init__(self, memory_type: str = "conversation_buffer", k: int = 10):
        self.memory_type = memory_type
        self.k = k
        self.conversation_history = []
        self.user_context = {}
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)

        # Keep only last k messages
        if len(self.conversation_history) > self.k:
            self.conversation_history = self.conversation_history[-self.k:]
    
    def get_conversation_context(self) -> List[Dict]:
        return self.conversation_history

    def update_user_context(self, context: Dict):
        self.user_context.update(context)


class ADKAgent(ABC):
    """Base ADK Agent with A2A capabilities"""
    
    def __init__(self, name: str, description: str, tools: List[Tool] = None, memory: Memory = None):
        self.name = name
        self.description = description
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.memory = memory or Memory()
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"agent.{name}")

        # A2A communication setup
        self.message_handlers = {}
        self.pending_requests = {}
        self.subscriptions = set()
        self.message_bus = None  # Will be injected

    def set_message_bus(self, message_bus):
        """Set the A2A message bus for this agent"""
        self.message_bus = message_bus

    async def initialize(self):
        """Initialize the agent"""
        self.logger.info(f"Initializing agent: {self.name}")
        await self.setup_a2a_communication()
        self.status = AgentStatus.IDLE

    async def setup_a2a_communication(self):
        """Set up A2A message bus connection"""
        if self.message_bus:
            await self.message_bus.register_agent(self)
            self.logger.info(f"Agent {self.name} registered with A2A message bus")
        else:
            self.logger.warning(f"No message bus set for agent {self.name}")

    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming requests"""
        pass

    async def send_a2a_message(self, to_agent: str, message_type: MessageType, payload: Dict[str, Any], conversation_id: str = None) -> str:
        """Send A2A message to another agent"""
        message = A2AMessage(
            id=self._generate_message_id(),
            from_agent=self.name,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow()
        )

        # Store correlation_id for responses
        if message_type == MessageType.REQUEST:
            message.correlation_id = message.id

        # Publish to message bus
        await self._publish_message(message)
        return message.id

    async def handle_a2a_message(self, message: A2AMessage):
        """Handle incoming A2A messages"""
        self.logger.info(f"Received A2A message from {message.from_agent}: {message.message_type.value}")
        
        if message.message_type == MessageType.REQUEST:
            response_data = await self.process_a2a_request(message)
            if response_data:
                # Send response back
                response_message = A2AMessage(
                    id=self._generate_message_id(),
                    from_agent=self.name,
                    to_agent=message.from_agent,
                    message_type=MessageType.RESPONSE,
                    payload=response_data,
                    conversation_id=message.conversation_id,
                    correlation_id=message.id,  # Link response to original request
                    timestamp=datetime.utcnow()
                )
                await self._publish_message(response_message)
        elif message.message_type == MessageType.RESPONSE:
            await self.handle_a2a_response(message)

    @abstractmethod
    async def process_a2a_request(self, message: A2AMessage) -> Dict[str, Any]:
        """Process A2A requests from other agents"""
        pass

    async def handle_a2a_response(self, message: A2AMessage):
        """Handle A2A responses"""
        # Match with pending requests using correlation_id
        if message.correlation_id in self.pending_requests:
            future = self.pending_requests.pop(message.correlation_id)
            if not future.done():
                future.set_result(message.payload)
        else:
            self.logger.warning(f"Received response {message.correlation_id} but no pending request found")

    def add_tool(self, tool: Tool):
        """Add a tool to the agent"""
        self.tools[tool.name] = tool

    async def use_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not available")
        
        self.logger.info(f"Using tool: {tool_name}")
        return await self.tools[tool_name].execute(**kwargs)

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        from uuid import uuid4
        return str(uuid4())

    async def _publish_message(self, message: A2AMessage):
        """Publish message to A2A message bus"""
        if self.message_bus:
            await self.message_bus.publish_message(message)
        else:
            self.logger.error("No message bus available for publishing message")

    async def send_request_and_wait(self, to_agent: str, action: str, parameters: Dict[str, Any], conversation_id: str = None, timeout: float = 30.0) -> Dict[str, Any]:
        """Send A2A request and wait for response"""
        payload = {
            "action": action,
            "parameters": parameters
        }
        
        message_id = await self.send_a2a_message(
            to_agent=to_agent,
            message_type=MessageType.REQUEST,
            payload=payload,
            conversation_id=conversation_id
        )

        # Create future for response
        response_future = asyncio.Future()
        self.pending_requests[message_id] = response_future

        try:
            response = await asyncio.wait_for(response_future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            self.pending_requests.pop(message_id, None)
            return {"status": "timeout", "message": f"No response from {to_agent} within {timeout} seconds"}
        except Exception as e:
            self.pending_requests.pop(message_id, None)
            return {"status": "error", "message": f"Error waiting for response: {str(e)}"}