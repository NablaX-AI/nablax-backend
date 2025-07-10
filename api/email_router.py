"""
Email Router - FastAPI routes for email-related operations
Wraps email agent functionality with FastAPI endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging

from schemas import DoTaskRequest, ServerToolRequest
from agents.agent import process_task, get_agent_capabilities

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["email"])

@router.post("/do-task")
async def email_do_task(request: DoTaskRequest):
    """
    Process email-related tasks using the email agent.
    
    This endpoint handles:
    - Email draft generation
    - Email reply generation
    - Email analysis and processing
    """
    try:
        result = await process_task(request.input_data)
        return result
    except Exception as e:
        logger.error(f"Email task processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-reply")
async def generate_reply(request: dict):
    """
    Legacy endpoint for email reply generation.
    Maintained for backward compatibility.
    """
    try:
        # Convert legacy format to standard format
        input_data = {
            "user_request": request.get("original_mail", ""),
            "context": request.get("context", {})
        }
        
        result = await process_task(input_data)
        return result
    except Exception as e:
        logger.error(f"Email reply generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities")
async def get_capabilities():
    """Get email processing capabilities."""
    try:
        capabilities = await get_agent_capabilities()
        return capabilities
    except Exception as e:
        logger.error(f"Failed to get email capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools")
async def get_email_tools():
    """Get available email processing tools."""
    try:
        from agents.mcp_manager import get_available_mcp_tools
        tools = await get_available_mcp_tools()
        return {
            "tools": tools,
            "total": len(tools)
        }
    except Exception as e:
        logger.error(f"Failed to get email tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_email_templates():
    """Get email templates."""
    try:
        from agents.mcp_manager import get_mcp_resource
        templates = await get_mcp_resource("email://templates")
        return templates
    except Exception as e:
        logger.error(f"Failed to get email templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))