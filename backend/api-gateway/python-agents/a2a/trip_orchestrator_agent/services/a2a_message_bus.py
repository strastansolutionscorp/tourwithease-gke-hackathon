# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class MessageStatus(Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"
    ACKNOWLEDGED = "acknowledged"

@dataclass
class A2AMessage:
    """A2A Protocol compliant message structure"""
    id: str
    conversation_id: str
    from_agent: str
    to_agent: str
    message_type: str
    payload: Dict[str, Any]
    protocol_version: str = "A2A/1.0"
    timestamp: str = None
    priority: MessagePriority = MessagePriority.NORMAL
    ttl_seconds: int = 300
    routing_history: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.routing_history is None:
            self.routing_history = []
    
    def add_routing_hop(self, node: str, action: str = "routed"):
        """Add routing hop to message history"""
        self.routing_history.append({
            "node": node,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
    
    def is_expired(self) -> bool:
        """Check if message has expired based on TTL"""
        created_time = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
        return datetime.now() > created_time + timedelta(seconds=self.ttl_seconds)

class A2AMessageBus:
    """Enhanced A2A Message Bus for agent communication"""
    
    def __init__(self):
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.active_conversations: Dict[str, Dict] = {}
        self.agent_registry: Dict[str, Dict] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.routing_table: Dict[str, str] = {}
        self.message_history: List[A2AMessage] = []
        self.subscribers: Dict[str, List[str]] = {}
        self.is_running = False
        
    async def start(self):
        """Start the message bus processing loop"""
        self.is_running = True
        logger.info("🚌 A2A Message Bus started")
        
        # Start message processing task
        asyncio.create_task(self._process_message_queue())
        asyncio.create_task(self._cleanup_expired_messages())
    
    async def stop(self):
        """Stop the message bus"""
        self.is_running = False
        logger.info("🛑 A2A Message Bus stopped")
    
    def register_agent(self, agent_name: str, agent_info: Dict[str, Any]):
        """Register an agent with the message bus"""
        self.agent_registry[agent_name] = {
            **agent_info,
            "registered_at": datetime.now().isoformat(),
            "status": "active",
            "message_count": 0
        }
        logger.info(f"📝 Registered agent: {agent_name}")
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler
        logger.info(f"🔧 Registered handler for message type: {message_type}")
    
    async def send_message(self, 
                          from_agent: str,
                          to_agent: str,
                          message_type: str,
                          payload: Dict[str, Any],
                          conversation_id: Optional[str] = None,
                          priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """Send an A2A message through the bus"""
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        message = A2AMessage(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            priority=priority
        )
        
        # Add to routing history
        message.add_routing_hop("message_bus", "queued")
        
        # Track conversation
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = {
                "participants": [from_agent, to_agent],
                "started_at": datetime.now().isoformat(),
                "message_count": 0,
                "status": "active"
            }
        
        self.active_conversations[conversation_id]["message_count"] += 1
        
        # Update agent message counts
        if from_agent in self.agent_registry:
            self.agent_registry[from_agent]["message_count"] += 1
        
        # Queue message for processing
        await self.message_queue.put(message)
        
        logger.info(f"📨 Message queued: {from_agent} → {to_agent} ({message_type})")
        return message.id
    
    async def broadcast_message(self,
                               from_agent: str,
                               message_type: str,
                               payload: Dict[str, Any],
                               target_agents: Optional[List[str]] = None) -> List[str]:
        """Broadcast message to multiple agents"""
        
        if target_agents is None:
            target_agents = list(self.agent_registry.keys())
        
        message_ids = []
        conversation_id = str(uuid.uuid4())
        
        for agent in target_agents:
            if agent != from_agent:  # Don't send to self
                message_id = await self.send_message(
                    from_agent=from_agent,
                    to_agent=agent,
                    message_type=message_type,
                    payload=payload,
                    conversation_id=conversation_id,
                    priority=MessagePriority.HIGH
                )
                message_ids.append(message_id)
        
        logger.info(f"📡 Broadcast message from {from_agent} to {len(target_agents)} agents")
        return message_ids
    
    async def _process_message_queue(self):
        """Process messages from the queue"""
        while self.is_running:
            try:
                # Get message from queue with timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Check if message expired
                if message.is_expired():
                    logger.warning(f"⏰ Message expired: {message.id}")
                    continue
                
                # Route message
                await self._route_message(message)
                
            except asyncio.TimeoutError:
                continue  # No messages in queue
            except Exception as e:
                logger.error(f"❌ Error processing message queue: {e}")
    
    async def _route_message(self, message: A2AMessage):
        """Route message to destination agent"""
        try:
            message.add_routing_hop("message_bus", "routing")
            
            # Check if target agent is registered
            if message.to_agent not in self.agent_registry:
                logger.error(f"❌ Target agent not registered: {message.to_agent}")
                return
            
            # Handle different message types
            if message.message_type in self.message_handlers:
                handler = self.message_handlers[message.message_type]
                await handler(message)
            else:
                # Default HTTP delivery
                await self._deliver_http_message(message)
            
            # Store in history
            self.message_history.append(message)
            
            # Cleanup old messages (keep last 1000)
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-1000:]
                
        except Exception as e:
            logger.error(f"❌ Error routing message {message.id}: {e}")
    
    async def _deliver_http_message(self, message: A2AMessage):
        """Deliver message via HTTP to target agent"""
        import httpx
        
        agent_info = self.agent_registry[message.to_agent]
        agent_url = agent_info.get("url")
        
        if not agent_url:
            logger.error(f"❌ No URL configured for agent: {message.to_agent}")
            return
        
        # Prepare A2A compliant payload
        payload = {
            "a2a_message": asdict(message),
            "message": message.payload.get("message", ""),
            "context": message.payload.get("context", {}),
            "routing_metadata": {
                "message_id": message.id,
                "conversation_id": message.conversation_id,
                "from_agent": message.from_agent,
                "protocol_version": message.protocol_version
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{agent_url}/chat",
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-A2A-Message-ID": message.id,
                        "X-A2A-From-Agent": message.from_agent,
                        "X-A2A-Protocol-Version": message.protocol_version
                    }
                )
                response.raise_for_status()
                
                message.add_routing_hop(message.to_agent, "delivered")
                logger.info(f"✅ Message delivered: {message.id} to {message.to_agent}")
                
        except Exception as e:
            message.add_routing_hop(message.to_agent, "failed")
            logger.error(f"❌ Failed to deliver message {message.id}: {e}")
    
    async def _cleanup_expired_messages(self):
        """Cleanup expired messages and conversations"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Clean up expired conversations
                expired_conversations = []
                for conv_id, conv_info in self.active_conversations.items():
                    started_time = datetime.fromisoformat(conv_info["started_at"])
                    if datetime.now() > started_time + timedelta(hours=1):  # 1 hour timeout
                        expired_conversations.append(conv_id)
                
                for conv_id in expired_conversations:
                    del self.active_conversations[conv_id]
                
                if expired_conversations:
                    logger.info(f"🧹 Cleaned up {len(expired_conversations)} expired conversations")
                    
            except Exception as e:
                logger.error(f"❌ Error in cleanup task: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            "registered_agents": len(self.agent_registry),
            "active_conversations": len(self.active_conversations),
            "message_queue_size": self.message_queue.qsize(),
            "total_messages_processed": len(self.message_history),
            "message_handlers": list(self.message_handlers.keys()),
            "agents": {name: info.get("message_count", 0) for name, info in self.agent_registry.items()}
        }

# Global message bus instance
message_bus = A2AMessageBus()
