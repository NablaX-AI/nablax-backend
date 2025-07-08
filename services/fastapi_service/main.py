from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from app.models.schemas import DoTaskRequest

app = FastAPI(
    title="Nablax API Gateway",
    description="External entry point for intelligent task processing using MCP architecture",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://localhost:8001")

@app.get("/")
async def root():
    return {
        "message": "Nablax API Gateway", 
        "version": "1.0.0",
        "architecture": "MCP-based three-tier system",
        "protocol": "Model Context Protocol (MCP)"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "service": "fastapi_gateway",
        "architecture": "MCP",
        "agent_url": AGENT_SERVICE_URL
    }

@app.post("/do-task")
async def do_task(request: DoTaskRequest):
    """
    Generic task processing endpoint with automatic intent detection.
    
    The Agent Service will:
    1. Analyze the input data to determine task type
    2. Select appropriate MCP tool from available tools
    3. Execute the task via MCP protocol
    4. Return the raw result without additional formatting
    
    Flow: Client -> FastAPI -> Agent (Tool Selection) -> MCP Tool -> Raw Response
    """
    try:
        # Forward request directly to agent service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENT_SERVICE_URL}/agent/do-task",
                json=request.dict(),
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Agent service error: {response.text}"
                )
            
            # Return agent response directly without additional processing
            return response.json()
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Agent service timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Agent service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/capabilities")
async def get_capabilities():
    """
    Get system capabilities and available MCP tools.
    """
    try:
        # Query agent service for available tools and capabilities
        async with httpx.AsyncClient() as client:
            tools_response = await client.get(
                f"{AGENT_SERVICE_URL}/agent/tools",
                timeout=10.0
            )
            
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
            else:
                tools_data = {"available_tools": [], "error": "Failed to fetch tools"}
        
        return {
            "system_info": {
                "name": "Nablax API Gateway",
                "version": "1.0.0",
                "architecture": "MCP-based microservices",
                "protocol": "Model Context Protocol (MCP)"
            },
            "endpoints": {
                "main_task": "/do-task",
                "health": "/health",
                "capabilities": "/capabilities",
                "debug": "/debug/mcp-flow"
            },
            "agent_capabilities": tools_data,
            "mcp_compliant": True
        }
        
    except Exception as e:
        return {
            "system_info": {
                "name": "Nablax API Gateway",
                "version": "1.0.0",
                "architecture": "MCP-based microservices"
            },
            "error": f"Failed to fetch full capabilities: {str(e)}",
            "basic_endpoints": ["/do-task", "/health", "/capabilities"]
        }

@app.get("/debug/mcp-flow")
async def debug_mcp_flow():
    """
    Debug endpoint to show the MCP flow and architecture.
    """
    return {
        "mcp_architecture": {
            "flow": [
                "1. Client submits request to FastAPI Gateway (/do-task)",
                "2. FastAPI forwards to Agent Service",
                "3. Agent analyzes input data and detects task type",
                "4. Agent selects appropriate MCP tool from available tools",
                "5. Agent calls selected MCP tool via MCP Client",
                "6. MCP Server processes request (LLM, tools, resources)",
                "7. Raw response flows back: MCP -> Agent -> FastAPI -> Client"
            ],
            "services": {
                "fastapi_gateway": {
                    "port": 8000,
                    "role": "External API entry point",
                    "endpoints": ["/do-task"],
                    "note": "No response formatting - direct passthrough"
                },
                "agent_service": {
                    "port": 8001,
                    "role": "Task detection and MCP tool selection",
                    "protocol": "MCP Client",
                    "endpoints": ["/agent/do-task"],
                    "features": ["intelligent_tool_selection", "task_detection"]
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
            "communication": "Agent ↔ MCP Server via stdio/subprocess",
            "response_handling": "Raw passthrough - no additional formatting"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)