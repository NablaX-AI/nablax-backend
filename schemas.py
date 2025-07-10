"""
Common Request/Response Schemas
Shared data models for the FastAPI application
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional

class DoTaskRequest(BaseModel):
    """Request for generic task processing"""
    input_data: Dict[str, Any]
    
class ServerToolRequest(BaseModel):
    """Request for direct MCP server tool calls"""
    arguments: Dict[str, Any]