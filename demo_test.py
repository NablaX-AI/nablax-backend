#!/usr/bin/env python3
"""
Demo test script to show the complete functionality.
"""

import asyncio
import httpx
import json

async def demo_test():
    """Complete demo of the system."""
    
    print("🎯 Nablax Agent Service Demo")
    print("=" * 50)
    
    # Step 1: Check services
    print("1️⃣ Checking Services...")
    async with httpx.AsyncClient() as client:
        try:
            health_response = await client.get("http://localhost:8001/health")
            if health_response.status_code == 200:
                print("✅ Agent Service: Running")
            else:
                print("❌ Agent Service: Not running")
                return
                
            # Check MCP
            debug_response = await client.get("http://localhost:8001/agent/debug/tools")
            if debug_response.status_code == 200:
                debug_data = debug_response.json()
                print("✅ MCP Server: Connected")
                
                # Show tools
                mcp_responses = debug_data.get("mcp_server_responses", {})
                total_tools = sum(info.get("tool_count", 0) for info in mcp_responses.values())
                print(f"📋 Available tools: {total_tools}")
                
                for service_name, info in mcp_responses.items():
                    print(f"  Service: {service_name}")
                    tools = info.get("tools", [])
                    for tool in tools:
                        name = tool.get('name', 'Unknown')
                        desc = tool.get('description', 'No description')
                        print(f"    • {name}: {desc}")
                        
        except Exception as e:
            print(f"❌ Service check failed: {e}")
            return
    
        # Step 2: Demo test cases
        print("\n2️⃣ Testing Natural Language Input...")
        
        test_cases = [
            "帮我回复这封邮件，用专业的语气：Hi, I would like to schedule a meeting.",
            "紧急！请帮我回复：Server is down, need help!",
            "帮我用轻松的语气回复：Hey, how's it going?",
            "我需要写一封邮件回复，原邮件内容是：Thanks for the presentation."
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_input[:50]}...")
            
            request_data = {
                "input_data": {
                    "user_request": test_input
                }
            }
            
            try:
                response = await client.post(
                    "http://localhost:8001/agent/do-task",
                    json=request_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ Success: Tool selected and executed")
                        data = result.get("data", {})
                        
                        # Show MCP result info
                        if "mcp_result_type" in result:
                            print(f"🔧 MCP Result Type: {result.get('mcp_result_type')}")
                        
                        # Show raw MCP result
                        if "raw_mcp_result" in result:
                            raw_result = result.get('raw_mcp_result', '')
                            if len(raw_result) > 300:
                                print(f"📦 Raw MCP Result: {raw_result[:300]}...")
                            else:
                                print(f"📦 Raw MCP Result: {raw_result}")
                        
                        # Show data section
                        if "data" in result:
                            data = result["data"]
                            if "reply_subject" in data:
                                print(f"📧 Subject: {data.get('reply_subject')}")
                            
                            if "reply_body" in data:
                                body = data.get('reply_body', '')
                                if len(body) > 200:
                                    print(f"📝 Body: {body[:200]}...")
                                else:
                                    print(f"📝 Body: {body}")
                        
                        # Show additional metadata
                        for key, value in result.items():
                            if key not in ['success', 'raw_mcp_result', 'mcp_result_type', 'data']:
                                print(f"📋 {key}: {value}")
                            
                    else:
                        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Test failed: {e}")
    
    print("\n🎉 Demo completed!")
    print("\n💡 You can now use:")
    print("  - python test_interactive.py  # Interactive testing")
    print("  - python test_quick.py       # Quick predefined tests")
    print("  - python test_quick.py 'your custom input'  # Custom test")
    print("  - python check_services.py   # Service status check")

if __name__ == "__main__":
    asyncio.run(demo_test())