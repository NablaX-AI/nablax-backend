"""
Agent Service - Simplified MCP Configuration System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from mcp_client import MCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nablax Agent Service",
    description="Simplified MCP configuration system",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MCP configuration
MCP_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "mcp.config")
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

# Load configuration on startup
load_mcp_config()

@app.get("/")
async def root():
    return {
        "message": "Nablax Agent Service - Simplified MCP Config",
        "version": "2.1.0",
        "mcp_servers": len(mcp_servers),
        "server_names": list(mcp_servers.keys())
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "agent_service",
        "protocol": "MCP",
        "servers": len(mcp_servers),
        "server_names": list(mcp_servers.keys())
    }

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

async def call_mcp_server(server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call MCP server tool."""
    if server_name not in mcp_servers:
        raise ValueError(f"Server not found: {server_name}")
    
    server_info = mcp_servers[server_name]
    client = server_info['client']
    
    logger.info(f"🔧 Calling MCP server: {server_name}")
    logger.info(f"📤 Command: {server_info['command']} {' '.join(server_info['args'])}")
    logger.info(f"🛠️  Tool: {tool_name}")
    logger.info(f"📝 Arguments: {arguments}")
    
    try:
        async with client as mcp_session:
            result = await mcp_session.call_tool(tool_name, arguments)
            
            logger.info(f"✅ MCP call successful")
            
            # Return raw result
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
                "command": server_info['command'],
                "args": server_info['args'],
                "description": server_info['description']
            }
        }

@app.post("/agent/do-task")
async def do_task(request: dict):
    """Process task using MCP servers."""
    try:
        input_data = request.get("input_data", request)
        user_request = input_data.get("user_request", "")
        
        # Find appropriate server
        server_name = find_server_by_keywords(user_request)
        if not server_name:
            return {
                "success": False,
                "error": "No MCP servers available",
                "available_servers": list(mcp_servers.keys())
            }
        
        # Extract email content and tone
        original_email = user_request
        patterns = ["：", ":", "邮件", "内容是", "下面的"]
        for pattern in patterns:
            if pattern in user_request:
                parts = user_request.split(pattern)
                if len(parts) > 1:
                    original_email = parts[-1].strip()
                    break
        
        # Detect tone
        tone = "professional"
        if "轻松" in user_request or "casual" in user_request.lower():
            tone = "casual"
        elif "紧急" in user_request or "urgent" in user_request.lower():
            tone = "urgent"
        
        # Prepare arguments - context should be a string according to MCP server schema
        urgency = "high" if tone == "urgent" else "normal"
        context_str = f"Reply type: reply, Urgency: {urgency}"
        
        arguments = {
            "original_email": original_email or "User request",
            "tone": tone,
            "context": context_str
        }
        
        # Call MCP server
        result = await call_mcp_server(server_name, "generate_email_draft", arguments)
        return result
        
    except Exception as e:
        logger.error(f"❌ Task processing failed: {e}")
        return {
            "success": False,
            "error": f"Task processing error: {str(e)}",
            "available_servers": list(mcp_servers.keys())
        }

@app.get("/agent/servers")
async def list_servers():
    """List all MCP servers."""
    servers = []
    for server_name, server_info in mcp_servers.items():
        servers.append({
            "name": server_name,
            "command": server_info['command'],
            "args": server_info['args'],
            "description": server_info['description'],
            "keywords": server_info['keywords']
        })
    
    return {
        "servers": servers,
        "total": len(servers)
    }

@app.get("/agent/servers/{server_name}/tools")
async def get_server_tools(server_name: str):
    """Get tools from specific server."""
    if server_name not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"Server not found: {server_name}")
    
    try:
        server_info = mcp_servers[server_name]
        client = server_info['client']
        
        async with client as mcp_session:
            tools = await mcp_session.list_tools()
            
            return {
                "server_name": server_name,
                "tools": tools,
                "tool_count": len(tools)
            }
    
    except Exception as e:
        return {
            "server_name": server_name,
            "error": str(e),
            "tools": []
        }

@app.post("/agent/servers/{server_name}/tools/{tool_name}")
async def call_server_tool_direct(server_name: str, tool_name: str, request: dict):
    """Direct tool call."""
    arguments = request.get("arguments", {})
    result = await call_mcp_server(server_name, tool_name, arguments)
    return result

@app.post("/agent/config/reload")
async def reload_config():
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

@app.get("/agent/debug")
async def debug_info():
    """Debug information."""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)