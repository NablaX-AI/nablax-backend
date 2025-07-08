#!/usr/bin/env python3
"""
Quick service status check script.
"""

import asyncio
import httpx
import json

async def check_services():
    """Check if all services are running."""
    
    print("🔍 Checking Nablax Services Status")
    print("=" * 40)
    
    services = [
        {
            "name": "Agent Service",
            "url": "http://localhost:8001/health",
            "description": "Main agent service with LLM tool selection"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for service in services:
            try:
                response = await client.get(service["url"], timeout=5.0)
                if response.status_code == 200:
                    print(f"✅ {service['name']}: Running")
                else:
                    print(f"❌ {service['name']}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {service['name']}: Not running ({e})")
        
        # Check MCP server connectivity
        print("\n🔧 Checking MCP Server:")
        try:
            debug_response = await client.get("http://localhost:8001/agent/debug/tools", timeout=10.0)
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                print("✅ MCP Server: Connected")
                
                # Show tools
                mcp_responses = debug_data.get("mcp_server_responses", {})
                total_tools = sum(info.get("tool_count", 0) for info in mcp_responses.values())
                print(f"📋 Available tools: {total_tools}")
                
                for service_name, info in mcp_responses.items():
                    print(f"  Service: {service_name}")
                    print(f"    Tool count: {info.get('tool_count', 0)}")
                    tools = info.get("tools", [])
                    for tool in tools:
                        name = tool.get('name', 'Unknown')
                        desc = tool.get('description', 'No description')
                        print(f"    • {name}: {desc}")
                        
                        # Show schema info
                        schema = tool.get('input_schema', {})
                        if schema.get('required'):
                            print(f"      Required: {schema['required']}")
                        if schema.get('properties'):
                            props = list(schema['properties'].keys())
                            print(f"      Properties: {props}")
                        
            else:
                print(f"❌ MCP Server: HTTP {debug_response.status_code}")
        except Exception as e:
            print(f"❌ MCP Server: Not responding ({e})")
    
    print("\n💡 Service Commands:")
    print("Start Agent Service: PYTHONPATH='.:$PYTHONPATH' python -m uvicorn services.agent_service.main:app --reload --port 8001")
    print("Start MCP Server: python services/mail_draft_mcp_service/mcp_server.py")
    print("Interactive Test: python test_interactive.py")

if __name__ == "__main__":
    asyncio.run(check_services())