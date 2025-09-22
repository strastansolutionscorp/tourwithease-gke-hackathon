# Copyright 2025 Google LLC
# Licensed under the Apache License, Version 2.0

import asyncio
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class A2AAgentDiscovery:
    """A2A Agent Discovery Service"""
    
    def __init__(self, message_bus):
        self.message_bus = message_bus
        self.discovered_agents: Dict[str, Dict] = {}
        self.health_status: Dict[str, bool] = {}
        self.last_discovery: Optional[datetime] = None
        self.discovery_interval = 300  # 5 minutes
        
    async def discover_agents(self, agent_configs: Dict[str, Dict]) -> Dict[str, Dict]:
        """Discover agents and fetch their capabilities"""
        logger.info("🔍 Starting agent discovery...")
        
        discovered = {}
        
        for agent_name, agent_config in agent_configs.items():
            try:
                agent_url = agent_config["url"]
                
                # Fetch agent card
                agent_card = await self._fetch_agent_card(agent_url)
                
                if agent_card:
                    discovered[agent_name] = {
                        **agent_config,
                        "agent_card": agent_card,
                        "status": "available",
                        "discovered_at": datetime.now().isoformat(),
                        "capabilities": agent_card.get("capabilities", []),
                        "tools": [tool.get("name") for tool in agent_card.get("tools", [])],
                        "endpoints": agent_card.get("endpoints", [])
                    }
                    
                    # Register with message bus
                    self.message_bus.register_agent(agent_name, discovered[agent_name])
                    
                    self.health_status[agent_name] = True
                    logger.info(f"✅ Discovered agent: {agent_name}")
                    
                else:
                    self.health_status[agent_name] = False
                    logger.warning(f"⚠️ Agent card not found: {agent_name}")
                    
            except Exception as e:
                self.health_status[agent_name] = False
                logger.error(f"❌ Failed to discover agent {agent_name}: {e}")
        
        self.discovered_agents = discovered
        self.last_discovery = datetime.now()
        
        logger.info(f"🎯 Discovery complete: {len(discovered)} agents available")
        return discovered
    
    async def _fetch_agent_card(self, base_url: str) -> Optional[Dict]:
        """Fetch agent card from well-known endpoints"""
        agent_card_paths = [
            "/.well-known/agent_card",
            "/.well-known/agent-card.json"
        ]
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                for path in agent_card_paths:
                    try:
                        response = await client.get(f"{base_url}{path}")
                        if response.status_code == 200:
                            return response.json()
                    except:
                        continue
                return None
        except Exception:
            return None
    
    async def health_check_agents(self) -> Dict[str, bool]:
        """Check health of all discovered agents"""
        health_results = {}
        
        for agent_name, agent_info in self.discovered_agents.items():
            agent_url = agent_info["url"]
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{agent_url}/health")
                    health_results[agent_name] = response.status_code == 200
            except:
                health_results[agent_name] = False
        
        self.health_status = health_results
        return health_results
    
    async def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents that support a specific capability"""
        matching_agents = []
        
        for agent_name, agent_info in self.discovered_agents.items():
            if capability in agent_info.get("capabilities", []):
                matching_agents.append(agent_name)
        
        return matching_agents
    
    async def negotiate_capabilities(self, agent_name: str, required_capabilities: List[str]) -> Dict:
        """Negotiate capabilities with an agent"""
        if agent_name not in self.discovered_agents:
            return {"status": "agent_not_found"}
        
        agent_info = self.discovered_agents[agent_name]
        agent_capabilities = agent_info.get("capabilities", [])
        
        supported = [cap for cap in required_capabilities if cap in agent_capabilities]
        unsupported = [cap for cap in required_capabilities if cap not in agent_capabilities]
        
        return {
            "status": "success",
            "agent": agent_name,
            "requested_capabilities": required_capabilities,
            "supported_capabilities": supported,
            "unsupported_capabilities": unsupported,
            "support_percentage": len(supported) / len(required_capabilities) if required_capabilities else 0,
            "negotiated_at": datetime.now().isoformat()
        }
