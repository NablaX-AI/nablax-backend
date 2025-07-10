"""
General Agent - Multi-Task Processing
Handles various tasks including email drafts using MCP servers
"""

import logging
from typing import Dict, Any, Optional, List
import re

from .mcp_manager import call_mcp_tool, get_mcp_servers
from .email_utils import (
    extract_email_content, detect_tone, build_context_string,
    format_mcp_arguments, create_error_response
)

logger = logging.getLogger(__name__)

def detect_task_type(user_request: str) -> str:
    """
    Detect the type of task from user request.
    
    Args:
        user_request: User's input request
        
    Returns:
        Task type (email_draft, general_query, etc.)
    """
    user_request_lower = user_request.lower()
    
    # Email-related keywords
    email_keywords = [
        "email", "邮件", "reply", "回复", "draft", "草稿",
        "message", "信息", "mail", "写邮件", "发邮件"
    ]
    
    for keyword in email_keywords:
        if keyword in user_request_lower:
            return "email_draft"
    
    # Default to general query
    return "general_query"

def validate_input(input_data: Dict[str, Any]) -> bool:
    """
    Validate input data structure.
    
    Args:
        input_data: Input data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(input_data, dict):
        return False
    
    user_request = input_data.get("user_request", "")
    if not user_request or not isinstance(user_request, str):
        return False
    
    return True

async def process_task(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process various types of tasks.
    
    Args:
        input_data: Task input data containing user_request and optional context
        
    Returns:
        Task processing result
    """
    try:
        # Validate input
        if not validate_input(input_data):
            return create_error_response("Invalid input format. Expected dict with 'user_request' field.")
        
        user_request = input_data.get("user_request", "")
        context = input_data.get("context", {})
        
        # Detect task type
        task_type = detect_task_type(user_request)
        logger.info(f"Detected task type: {task_type} for request: {user_request[:50]}...")
        
        # Route to appropriate handler
        if task_type == "email_draft":
            return await handle_email_task(user_request, context)
        else:
            return await handle_general_task(user_request, context)
            
    except Exception as e:
        logger.error(f"Task processing failed: {e}")
        return create_error_response(f"Task processing error: {str(e)}")

async def handle_email_task(user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle email-related tasks.
    
    Args:
        user_request: User's request
        context: Additional context
        
    Returns:
        Email task result
    """
    try:
        # Extract email content and detect tone
        original_email = extract_email_content(user_request)
        tone = detect_tone(user_request)
        context_str = build_context_string(user_request, tone)
        
        # Prepare arguments for MCP call
        arguments = format_mcp_arguments(original_email, tone, context_str)
        
        logger.info(f"Processing email task with tone: {tone}")
        
        # Call MCP server for email draft generation
        result = await call_mcp_tool("generate_email_draft", arguments)
        
        if result.get("success"):
            # Add task type information
            result["task_type"] = "email_draft"
            result["detected_tone"] = tone
            result["extracted_content"] = original_email
            return result
        else:
            return create_error_response(
                "Email draft generation failed",
                {"mcp_error": result.get("error"), "task_type": "email_draft"}
            )
            
    except Exception as e:
        logger.error(f"Email task processing failed: {e}")
        return create_error_response(f"Email processing error: {str(e)}")

async def handle_general_task(user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle general tasks that don't fit specific categories.
    
    Args:
        user_request: User's request
        context: Additional context
        
    Returns:
        General task result
    """
    try:
        # For now, provide a general response
        # In the future, this could route to different MCP tools based on the request
        
        return {
            "success": True,
            "task_type": "general_query",
            "user_request": user_request,
            "data": {
                "message": "General task processing is not yet implemented",
                "suggestion": "For email-related tasks, try: 'help me reply to this email: [email content]'",
                "available_capabilities": [
                    "Email draft generation",
                    "Email reply generation", 
                    "Tone detection"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"General task processing failed: {e}")
        return create_error_response(f"General task error: {str(e)}")

async def get_agent_capabilities() -> Dict[str, Any]:
    """
    Get agent capabilities and available tasks.
    
    Returns:
        Agent capabilities information
    """
    try:
        servers = get_mcp_servers()
        
        return {
            "agent_type": "general_multi_task",
            "supported_tasks": [
                {
                    "type": "email_draft",
                    "description": "Generate email drafts and replies",
                    "keywords": ["email", "reply", "draft", "mail"],
                    "example": "help me reply to this email: Hello, I need assistance..."
                },
                {
                    "type": "general_query", 
                    "description": "General task processing (coming soon)",
                    "keywords": ["help", "assist", "question"],
                    "example": "help me with..."
                }
            ],
            "mcp_integration": {
                "servers": list(servers.keys()),
                "available_tools": ["generate_email_draft"]
            },
            "features": [
                "Automatic task type detection",
                "Email content extraction",
                "Tone detection",
                "MCP server integration"
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get agent capabilities: {e}")
        return create_error_response(f"Failed to get capabilities: {str(e)}")

async def test_email_functionality(test_request: str = None) -> Dict[str, Any]:
    """
    Test the email functionality with a sample request.
    
    Args:
        test_request: Optional test request, uses default if not provided
        
    Returns:
        Test result
    """
    if not test_request:
        test_request = "help me reply to this email: Hello, I hope you're doing well. I wanted to follow up on our meeting last week."
    
    try:
        input_data = {"user_request": test_request}
        result = await process_task(input_data)
        
        return {
            "test_success": True,
            "test_request": test_request,
            "result": result
        }
        
    except Exception as e:
        return {
            "test_success": False,
            "test_request": test_request,
            "error": str(e)
        }