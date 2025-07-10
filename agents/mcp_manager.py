"""
MCP Manager - Global MCP Server Configuration and Orchestration
Centralized management of all MCP servers and their configurations
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .mcp_client import MCPClient

logger = logging.getLogger(__name__)

# Global MCP configuration
MCP_CONFIG_FILE = "mcp.config"
mcp_servers = {}

def load_mcp_config():
    """Load MCP servers from configuration file."""
    global mcp_servers
    
    try:
        if not os.path.exists(MCP_CONFIG_FILE):
            logger.error(f"❌ MCP config file not found: {MCP_CONFIG_FILE}")
            return
        
        with open(MCP_CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        servers_config = config.get('mcpServers', {})
        
        for server_name, server_config in servers_config.items():
            command = server_config.get('command', 'python')
            args = server_config.get('args', [])
            description = server_config.get('description', f"MCP Server: {server_name}")
            keywords = server_config.get('keywords', [])
            
            # Create MCP client
            client = MCPClient(
                server_command=command,
                server_args=args,
                timeout=30
            )
            
            mcp_servers[server_name] = {
                'client': client,
                'command': command,
                'args': args,
                'description': description,
                'keywords': keywords
            }
            
            logger.info(f"✅ Loaded MCP server: {server_name}")
        
        logger.info(f"📋 Loaded {len(mcp_servers)} MCP servers")
        
    except Exception as e:
        logger.error(f"❌ Failed to load MCP config: {e}")

def get_mcp_servers() -> Dict[str, Dict[str, Any]]:
    """Get all loaded MCP servers."""
    return mcp_servers

def find_server_by_keywords(text: str) -> Optional[str]:
    """Find MCP server by keyword matching."""
    text_lower = text.lower()
    
    for server_name, server_info in mcp_servers.items():
        keywords = server_info.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return server_name
    
    # Fallback to first server if no match
    return next(iter(mcp_servers.keys())) if mcp_servers else None

def get_mcp_client(server_name: Optional[str] = None) -> Optional[MCPClient]:
    """
    Get MCP client for specified server.
    
    Args:
        server_name: Name of the server, if None uses first available
        
    Returns:
        MCP client instance or None
    """
    if not mcp_servers:
        load_mcp_config()
    
    if server_name and server_name in mcp_servers:
        return mcp_servers[server_name]['client']
    elif mcp_servers:
        # Return first available server
        first_server = next(iter(mcp_servers.keys()))
        return mcp_servers[first_server]['client']
    
    return None

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any], server_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Call MCP server tool.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments
        server_name: Server name, if None uses keyword matching or first available
        
    Returns:
        Tool call result
    """
    try:
        # Find server if not specified
        if not server_name:
            if "user_request" in arguments:
                server_name = find_server_by_keywords(arguments["user_request"])
            elif "original_email" in arguments:
                server_name = find_server_by_keywords(arguments["original_email"])
            else:
                server_name = next(iter(mcp_servers.keys())) if mcp_servers else None
        
        if not server_name or server_name not in mcp_servers:
            return {
                "success": False,
                "error": "No suitable MCP server found",
                "available_servers": list(mcp_servers.keys())
            }
        
        server_info = mcp_servers[server_name]
        client = server_info['client']
        
        logger.info(f"🔧 Calling MCP server: {server_name}")
        logger.info(f"📤 Command: {server_info['command']} {' '.join(server_info['args'])}")
        logger.info(f"🛠️  Tool: {tool_name}")
        logger.info(f"📝 Arguments: {arguments}")
        
        async with client as mcp_session:
            result = await mcp_session.call_tool(tool_name, arguments)
            
            logger.info(f"✅ MCP call successful")
            
            return {
                "success": True,
                "server_name": server_name,
                "tool_name": tool_name,
                "raw_mcp_result": str(result),
                "mcp_result_type": str(type(result)),
                "server_info": {
                    "command": server_info['command'],
                    "args": server_info['args'],
                    "description": server_info['description']
                },
                "data": {
                    "reply_subject": "MCP Response",
                    "reply_body": str(result)
                }
            }
    
    except Exception as e:
        logger.error(f"❌ MCP call failed: {e}")
        return {
            "success": False,
            "server_name": server_name,
            "tool_name": tool_name,
            "error": str(e),
            "server_info": {
                "command": server_info.get('command', 'unknown'),
                "args": server_info.get('args', []),
                "description": server_info.get('description', 'unknown')
            } if server_name and server_name in mcp_servers else {}
        }

async def get_available_mcp_tools(server_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get available tools from MCP server.
    
    Args:
        server_name: Server name, if None gets from all servers
        
    Returns:
        List of available tools
    """
    tools = []
    
    try:
        if server_name and server_name in mcp_servers:
            # Get tools from specific server
            server_info = mcp_servers[server_name]
            client = server_info['client']
            
            async with client as mcp_session:
                server_tools = await mcp_session.list_tools()
                for tool in server_tools:
                    tool['server_name'] = server_name
                tools.extend(server_tools)
        else:
            # Get tools from all servers
            for name, server_info in mcp_servers.items():
                try:
                    client = server_info['client']
                    async with client as mcp_session:
                        server_tools = await mcp_session.list_tools()
                        for tool in server_tools:
                            tool['server_name'] = name
                        tools.extend(server_tools)
                except Exception as e:
                    logger.error(f"Failed to get tools from {name}: {e}")
        
        return tools
        
    except Exception as e:
        logger.error(f"Failed to get available tools: {e}")
        return []

async def get_mcp_resource(resource_uri: str, server_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get resource from MCP server.
    
    Args:
        resource_uri: URI of the resource
        server_name: Server name, if None uses first available
        
    Returns:
        Resource data
    """
    try:
        if not server_name:
            server_name = next(iter(mcp_servers.keys())) if mcp_servers else None
        
        if not server_name or server_name not in mcp_servers:
            return {
                "success": False,
                "error": "No suitable MCP server found",
                "available_servers": list(mcp_servers.keys())
            }
        
        server_info = mcp_servers[server_name]
        client = server_info['client']
        
        async with client as mcp_session:
            result = await mcp_session.read_resource(resource_uri)
            
            return {
                "success": True,
                "server_name": server_name,
                "resource_uri": resource_uri,
                "data": result
            }
    
    except Exception as e:
        logger.error(f"Failed to get resource {resource_uri}: {e}")
        return {
            "success": False,
            "error": str(e),
            "resource_uri": resource_uri
        }

async def reload_mcp_config() -> Dict[str, Any]:
    """Reload MCP configuration."""
    try:
        load_mcp_config()
        return {
            "success": True,
            "message": "Configuration reloaded",
            "servers": len(mcp_servers),
            "server_names": list(mcp_servers.keys())
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_mcp_debug_info() -> Dict[str, Any]:
    """Get MCP debug information."""
    return {
        "config_file": MCP_CONFIG_FILE,
        "config_exists": os.path.exists(MCP_CONFIG_FILE),
        "servers": {
            name: {
                "command": info['command'],
                "args": info['args'],
                "description": info['description'],
                "keywords": info['keywords']
            }
            for name, info in mcp_servers.items()
        }
    }

# Initialize MCP configuration on module import
load_mcp_config()