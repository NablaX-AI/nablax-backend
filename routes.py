"""
Application Routes
Function-based route definitions for the FastAPI application
"""

from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional, List
import logging

from schemas import DoTaskRequest, ServerToolRequest
from agents.mcp_manager import (
    get_mcp_servers, call_mcp_tool, get_available_mcp_tools,
    get_mcp_resource, reload_mcp_config, get_mcp_debug_info
)
from agents.agent import process_task

logger = logging.getLogger(__name__)

def setup_main_routes(app: FastAPI):
    """Setup main application routes."""
    
    @app.get("/")
    async def root():
        servers = get_mcp_servers()
        return {
            "message": "Nablax Backend API - Function-based Architecture", 
            "version": "2.0.0",
            "architecture": "MCP-based three-tier system",
            "protocol": "Model Context Protocol (MCP)",
            "mcp_servers": len(servers),
            "server_names": list(servers.keys())
        }

    @app.get("/health")
    async def health():
        servers = get_mcp_servers()
        return {
            "status": "healthy", 
            "service": "nablax_backend",
            "architecture": "MCP Function-based",
            "servers": len(servers),
            "server_names": list(servers.keys())
        }

    @app.post("/do-task")
    async def do_task(request: DoTaskRequest):
        """
        Generic task processing endpoint with automatic intent detection.
        
        The system will:
        1. Analyze the input data to determine task type
        2. Route to appropriate agent (currently email agent)
        3. Execute the task via MCP protocol
        4. Return the result
        
        Flow: Client -> FastAPI -> Agent -> MCP Tool -> Response
        """
        try:
            # Route to general agent for processing
            result = await process_task(request.input_data)
            return result
            
        except Exception as e:
            logger.error(f"❌ Task processing failed: {e}")
            servers = get_mcp_servers()
            return {
                "success": False,
                "error": f"Task processing error: {str(e)}",
                "available_servers": list(servers.keys())
            }

def setup_agent_routes(app: FastAPI):
    """Setup agent-related routes."""
    
    @app.post("/agent/do-task")
    async def agent_do_task(request: dict):
        """Process task using agents (agent endpoint)."""
        try:
            # Convert dict to standard format for processing
            input_data = request.get("input_data", request)
            result = await process_task(input_data)
            return result
        except Exception as e:
            logger.error(f"❌ Agent task processing failed: {e}")
            return {
                "success": False,
                "error": f"Agent processing error: {str(e)}"
            }

    @app.get("/agent/servers")
    async def list_servers():
        """List all MCP servers."""
        servers = get_mcp_servers()
        server_list = []
        
        for server_name, server_info in servers.items():
            server_list.append({
                "name": server_name,
                "command": server_info['command'],
                "args": server_info['args'],
                "description": server_info['description'],
                "keywords": server_info['keywords']
            })
        
        return {
            "servers": server_list,
            "total": len(server_list)
        }

    @app.get("/agent/servers/{server_name}/tools")
    async def get_server_tools(server_name: str):
        """Get tools from specific server."""
        servers = get_mcp_servers()
        if server_name not in servers:
            raise HTTPException(status_code=404, detail=f"Server not found: {server_name}")
        
        try:
            tools = await get_available_mcp_tools(server_name)
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
    async def call_server_tool_direct(server_name: str, tool_name: str, request: ServerToolRequest):
        """Direct tool call."""
        try:
            result = await call_mcp_tool(tool_name, request.arguments, server_name)
            return result
        except Exception as e:
            logger.error(f"❌ Direct tool call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "server_name": server_name,
                "tool_name": tool_name
            }

    @app.post("/agent/config/reload")
    async def reload_config():
        """Reload MCP configuration."""
        try:
            result = await reload_mcp_config()
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    @app.get("/agent/debug")
    async def debug_info():
        """Debug information."""
        return get_mcp_debug_info()

def setup_system_routes(app: FastAPI):
    """Setup system and debug routes."""
    
    @app.get("/capabilities")
    async def get_capabilities():
        """Get system capabilities and available MCP tools."""
        try:
            # Get tools from all servers
            all_tools = await get_available_mcp_tools()
            servers = get_mcp_servers()
            
            return {
                "system_info": {
                    "name": "Nablax Backend API",
                    "version": "2.0.0",
                    "architecture": "MCP-based function-based service",
                    "protocol": "Model Context Protocol (MCP)"
                },
                "endpoints": {
                    "main_task": "/do-task",
                    "agent_task": "/agent/do-task",
                    "email_routes": "/email/*",
                    "health": "/health",
                    "capabilities": "/capabilities",
                    "debug": "/debug/mcp-flow"
                },
                "mcp_tools": all_tools,
                "mcp_servers": list(servers.keys()),
                "mcp_compliant": True
            }
            
        except Exception as e:
            return {
                "system_info": {
                    "name": "Nablax Backend API",
                    "version": "2.0.0",
                    "architecture": "MCP-based function-based service"
                },
                "error": f"Failed to fetch full capabilities: {str(e)}",
                "basic_endpoints": ["/do-task", "/agent/do-task", "/email/*", "/health", "/capabilities"]
            }

    @app.get("/debug/mcp-flow")
    async def debug_mcp_flow():
        """Debug endpoint to show the MCP flow and architecture."""
        return {
            "mcp_architecture": {
                "flow": [
                    "1. Client submits request to FastAPI (/do-task)",
                    "2. FastAPI analyzes input and routes to appropriate agent",
                    "3. Agent processes request using business logic",
                    "4. Agent calls MCP server via function-based MCP client",
                    "5. MCP Server processes request (LLM, tools, resources)",
                    "6. Response flows back: MCP -> Agent -> FastAPI -> Client"
                ],
                "services": {
                    "main_fastapi": {
                        "port": 8000,
                        "role": "Single service with function-based architecture",
                        "endpoints": ["/do-task", "/agent/do-task", "/email/*", "/capabilities"],
                        "features": ["agent_routing", "mcp_integration", "function_based"]
                    },
                    "general_agent": {
                        "role": "Multi-task processing with email capabilities",
                        "features": ["task_detection", "tone_detection", "content_extraction", "mcp_orchestration"]
                    },
                    "mcp_functions": {
                        "role": "MCP server communication functions",
                        "features": ["server_management", "tool_calling", "resource_access"]
                    },
                    "mcp_server": {
                        "port": "stdio",
                        "role": "Tool execution and LLM integration",
                        "protocol": "MCP Server",
                        "available_tools": ["generate_email_draft", "future_tools"],
                        "resources": ["email_templates", "best_practices"]
                    }
                },
                "mcp_protocol": "2024-11-05",
                "communication": "FastAPI Functions ↔ MCP Server via stdio/subprocess",
                "architecture": "Function-based with agent routing"
            }
        }