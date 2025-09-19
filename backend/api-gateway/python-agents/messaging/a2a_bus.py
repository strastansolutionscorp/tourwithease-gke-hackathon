# messaging/a2a_bus.py
import redis.asyncio as redis
import json
import asyncio
from typing import Dict, Set, Callable

class A2AMessageBus:
    """A2A Protocol Message Bus using Redis"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.pubsub = None
        self.agents: Dict[str, 'ADKAgent'] = {}  # Forward reference
        self.subscriptions: Dict[str, Set[str]] = {}
        self._listening = False

    async def initialize(self):
        """Initialize Redis connection"""
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()
        print(f"A2A Message Bus initialized with Redis at {self.redis_url}")

    async def register_agent(self, agent):
        """Register an agent with the message bus"""
        self.agents[agent.name] = agent
        
        # Subscribe to agent's channel
        agent_channel = f"agent:{agent.name}"
        await self.pubsub.subscribe(agent_channel)
        self.subscriptions.setdefault(agent.name, set()).add(agent_channel)

        # Subscribe to broadcast channel
        broadcast_channel = "agents:broadcast"
        await self.pubsub.subscribe(broadcast_channel)
        self.subscriptions.setdefault(agent.name, set()).add(broadcast_channel)
        
        print(f"Agent '{agent.name}' registered and subscribed to channels")

    async def publish_message(self, message):
        """Publish A2A message"""
        # Import here to avoid circular import
        from agents.base_agent import A2AMessage
        
        # Publish to specific agent channel
        target_channel = f"agent:{message.to_agent}"
        message_data = json.dumps(message.to_dict())

        await self.redis_client.publish(target_channel, message_data)
        print(f"Published message from {message.from_agent} to {message.to_agent} via {target_channel}")

        # Store message for persistence/debugging
        await self.redis_client.lpush(
            f"messages:{message.conversation_id or 'default'}",
            message_data
        )
        await self.redis_client.expire(
            f"messages:{message.conversation_id or 'default'}",
            3600  # 1 hour expiry
        )

    async def broadcast_message(self, message):
        """Broadcast message to all agents"""
        broadcast_channel = "agents:broadcast"
        message_data = json.dumps(message.to_dict())
        await self.redis_client.publish(broadcast_channel, message_data)

    async def listen_for_messages(self):
        """Listen for incoming messages"""
        print("Starting to listen for A2A messages...")
        self._listening = True
        
        async for message in self.pubsub.listen():
            if not self._listening:
                break
                
            if message['type'] == 'message':
                try:
                    # Import here to avoid circular import
                    from agents.base_agent import A2AMessage
                    
                    message_data = json.loads(message['data'])
                    a2a_message = A2AMessage.from_dict(message_data)
                    
                    print(f"Routing message {a2a_message.id} to agent '{a2a_message.to_agent}'")

                    # Route message to appropriate agent
                    if a2a_message.to_agent in self.agents:
                        agent = self.agents[a2a_message.to_agent]
                        await agent.handle_a2a_message(a2a_message)
                    else:
                        print(f"No agent found for {a2a_message.to_agent}")
                        
                except Exception as e:
                    print(f"Error processing message: {e}")

    async def start_listening(self):
        """Start the message listener"""
        listen_task = asyncio.create_task(self.listen_for_messages())
        return listen_task

    async def stop_listening(self):
        """Stop the message listener"""
        self._listening = False
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
