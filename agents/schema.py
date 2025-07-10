"""
General Agent Schemas
Data models for multi-task agent processing
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class TaskRequest(BaseModel):
    """Request for general task processing"""
    user_request: str
    context: Optional[Dict[str, Any]] = {}
    task_type: Optional[str] = None  # Can be auto-detected or explicitly set

class TaskResponse(BaseModel):
    """Response from task processing"""
    success: bool
    task_type: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class AgentCapability(BaseModel):
    """Agent capability description"""
    type: str
    description: str
    keywords: List[str] = []
    example: Optional[str] = None

class EmailTaskData(BaseModel):
    """Data specific to email tasks"""
    detected_tone: str
    extracted_content: str
    original_request: str
    generated_draft: Optional[str] = None

class GeneralTaskData(BaseModel):
    """Data for general tasks"""
    message: str
    suggestion: Optional[str] = None
    available_capabilities: List[str] = []