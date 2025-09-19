# a2a/schemas/agent_card.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dataclasses import dataclass

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[str]] = None

class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    returns: Dict[str, Any]

class AgentEndpoint(BaseModel):
    path: str
    method: str
    description: str
    content_type: str = "application/json"

class AgentCard(BaseModel):
    name: str
    version: str
    description: str
    author: str
    created_date: str
    capabilities: List[str]
    tools: List[ToolSchema]
    endpoints: List[AgentEndpoint]
    communication_protocols: List[str]
    base_url: str
    health_check_endpoint: str
    authentication: Dict[str, Any]
    metadata: Dict[str, Any]
