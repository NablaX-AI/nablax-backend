"""
Email Utility Functions
Consolidated email processing utilities
"""

import re
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

def extract_email_content(user_request: str) -> str:
    """
    Extract email content from user request.
    
    Args:
        user_request: User's input request
        
    Returns:
        Extracted email content
    """
    patterns = ["：", ":", "邮件", "内容是", "下面的"]
    
    for pattern in patterns:
        if pattern in user_request:
            parts = user_request.split(pattern)
            if len(parts) > 1:
                return parts[-1].strip()
    
    return user_request

def detect_tone(user_request: str) -> str:
    """
    Detect tone from user request.
    
    Args:
        user_request: User's input request
        
    Returns:
        Detected tone (professional, casual, urgent, etc.)
    """
    user_request_lower = user_request.lower()
    
    if "轻松" in user_request or "casual" in user_request_lower:
        return "casual"
    elif "紧急" in user_request or "urgent" in user_request_lower:
        return "urgent"
    elif "正式" in user_request or "formal" in user_request_lower:
        return "formal"
    elif "友好" in user_request or "friendly" in user_request_lower:
        return "friendly"
    else:
        return "professional"

def detect_urgency(user_request: str, tone: str) -> str:
    """
    Detect urgency level from user request and tone.
    
    Args:
        user_request: User's input request
        tone: Detected tone
        
    Returns:
        Urgency level (high, normal, low)
    """
    user_request_lower = user_request.lower()
    
    if tone == "urgent" or "紧急" in user_request or "urgent" in user_request_lower:
        return "high"
    elif "慢" in user_request or "slow" in user_request_lower:
        return "low"
    else:
        return "normal"

def build_context_string(user_request: str, tone: str) -> str:
    """
    Build context string for MCP server.
    
    Args:
        user_request: User's input request
        tone: Detected tone
        
    Returns:
        Context string for MCP server
    """
    urgency = detect_urgency(user_request, tone)
    return f"Reply type: reply, Urgency: {urgency}"

def validate_email_request(input_data: Dict[str, Any]) -> bool:
    """
    Validate email request data.
    
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

def format_mcp_arguments(original_email: str, tone: str, context: str) -> Dict[str, Any]:
    """
    Format arguments for MCP server call.
    
    Args:
        original_email: Original email content
        tone: Email tone
        context: Context string
        
    Returns:
        Formatted arguments dictionary
    """
    return {
        "original_email": original_email or "User request",
        "tone": tone,
        "context": context
    }

def parse_mcp_response(mcp_result: Any) -> Dict[str, Any]:
    """
    Parse MCP server response.
    
    Args:
        mcp_result: Raw MCP server response
        
    Returns:
        Parsed response dictionary
    """
    return {
        "success": True,
        "raw_mcp_result": str(mcp_result),
        "mcp_result_type": str(type(mcp_result)),
        "data": {
            "reply_subject": "MCP Response",
            "reply_body": str(mcp_result)
        }
    }

def create_error_response(error_message: str, additional_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create error response.
    
    Args:
        error_message: Error message
        additional_info: Additional information
        
    Returns:
        Error response dictionary
    """
    response = {
        "success": False,
        "error": error_message
    }
    
    if additional_info:
        response.update(additional_info)
    
    return response

def get_supported_tones() -> List[str]:
    """Get list of supported email tones."""
    return ["professional", "casual", "urgent", "formal", "friendly"]

def get_supported_types() -> List[str]:
    """Get list of supported email types."""
    return ["reply", "draft", "forward", "thank_you", "follow_up"]