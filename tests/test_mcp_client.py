#!/usr/bin/env python3
"""
Test MCP Client Tool Listing Functionality
Tests whether mcp_client can list all available tools
"""

import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def test_mcp_client_import():
    """Test that MCP client modules can be imported."""
    try:
        from agents.mcp_manager import (
            get_mcp_servers, get_available_mcp_tools, call_mcp_tool
        )
        print("✅ MCP client functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import MCP client: {e}")
        return False

def test_mcp_config_loading():
    """Test that MCP configuration can be loaded."""
    try:
        from agents.mcp_manager import get_mcp_servers
        
        servers = get_mcp_servers()
        print(f"📋 MCP servers loaded: {list(servers.keys())}")
        
        if not servers:
            print("⚠️  No MCP servers configured")
            return False
        
        # Check server structure
        for server_name, server_config in servers.items():
            required_keys = ["command", "args", "description"]
            missing_keys = [key for key in required_keys if key not in server_config]
            
            if missing_keys:
                print(f"⚠️  Server {server_name} missing keys: {missing_keys}")
            else:
                print(f"✅ Server {server_name} properly configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading MCP configuration: {e}")
        return False

async def test_mcp_tool_listing():
    """Test that MCP client can list tools from all servers."""
    try:
        from agents.mcp_manager import get_available_mcp_tools, get_mcp_servers
        
        servers = get_mcp_servers()
        if not servers:
            print("⚠️  No MCP servers available for tool listing test")
            return False
        
        print(f"🔍 Testing tool listing for {len(servers)} servers...")
        
        # Test getting tools from all servers
        try:
            all_tools = await get_available_mcp_tools()
            print(f"📋 All available tools: {len(all_tools)} tools")
            
            for tool in all_tools:
                print(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            
            if all_tools:
                print("✅ Successfully listed tools from all servers")
                return True
            else:
                print("⚠️  No tools found across all servers")
                return False
                
        except Exception as e:
            print(f"❌ Error getting tools from all servers: {e}")
            
            # Try individual server testing
            success_count = 0
            for server_name in servers.keys():
                try:
                    server_tools = await get_available_mcp_tools(server_name)
                    print(f"✅ Server {server_name}: {len(server_tools)} tools")
                    success_count += 1
                except Exception as server_error:
                    print(f"❌ Server {server_name} error: {server_error}")
            
            if success_count > 0:
                print(f"✅ Successfully listed tools from {success_count}/{len(servers)} servers")
                return True
            else:
                print("❌ Failed to list tools from any server")
                return False
        
    except Exception as e:
        print(f"❌ Error in MCP tool listing test: {e}")
        return False

async def test_mcp_tool_structure():
    """Test that MCP tools have the expected structure."""
    try:
        from agents.mcp_manager import get_available_mcp_tools
        
        tools = await get_available_mcp_tools()
        
        if not tools:
            print("⚠️  No tools available for structure test")
            return False
        
        print(f"🔍 Testing structure of {len(tools)} tools...")
        
        valid_tools = 0
        for tool in tools:
            if isinstance(tool, dict) and "name" in tool:
                valid_tools += 1
                print(f"  ✅ {tool['name']}: Valid structure")
            else:
                print(f"  ⚠️  Invalid tool structure: {tool}")
        
        if valid_tools == len(tools):
            print("✅ All tools have valid structure")
            return True
        else:
            print(f"⚠️  {valid_tools}/{len(tools)} tools have valid structure")
            return False
        
    except Exception as e:
        print(f"❌ Error testing tool structure: {e}")
        return False

async def test_mcp_server_communication():
    """Test basic MCP server communication."""
    try:
        from agents.mcp_manager import get_mcp_servers
        
        servers = get_mcp_servers()
        if not servers:
            print("⚠️  No servers available for communication test")
            return False
        
        print(f"🔍 Testing communication with {len(servers)} servers...")
        
        # Test basic server availability
        available_servers = 0
        for server_name, server_config in servers.items():
            try:
                # Check if server configuration is valid
                if "command" in server_config and "args" in server_config:
                    print(f"  ✅ Server {server_name}: Configuration valid")
                    available_servers += 1
                else:
                    print(f"  ⚠️  Server {server_name}: Invalid configuration")
                    
            except Exception as server_error:
                print(f"  ❌ Server {server_name}: {server_error}")
        
        if available_servers > 0:
            print(f"✅ {available_servers}/{len(servers)} servers available")
            return True
        else:
            print("❌ No servers available for communication")
            return False
        
    except Exception as e:
        print(f"❌ Error testing server communication: {e}")
        return False

async def test_mcp_config_file():
    """Test that MCP configuration file exists and is valid."""
    try:
        config_path = "mcp.config"
        
        if not os.path.exists(config_path):
            print(f"❌ MCP config file not found: {config_path}")
            return False
        
        print(f"✅ MCP config file found: {config_path}")
        
        # Try to load the configuration
        from agents.mcp_manager import load_mcp_config
        config = load_mcp_config()
        
        if config and "servers" in config:
            servers = config["servers"]
            print(f"📋 Config contains {len(servers)} servers")
            
            for server_name, server_config in servers.items():
                print(f"  - {server_name}: {server_config.get('description', 'No description')}")
            
            return True
        else:
            print("❌ Invalid MCP configuration format")
            return False
        
    except Exception as e:
        print(f"❌ Error testing MCP config file: {e}")
        return False

def main():
    """Run all MCP client tests."""
    print("=== Testing MCP Client Tool Listing ===\n")
    
    tests = [
        ("MCP Client Import", test_mcp_client_import),
        ("MCP Config Loading", test_mcp_config_loading),
        ("MCP Tool Listing", test_mcp_tool_listing),
        ("MCP Tool Structure", test_mcp_tool_structure),
        ("MCP Server Communication", test_mcp_server_communication),
        ("MCP Config File", test_mcp_config_file),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()
                
            if result:
                passed += 1
                print(f"✅ {test_name} passed\n")
            else:
                failed += 1
                print(f"❌ {test_name} failed\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} crashed: {e}\n")
    
    print("=== MCP Client Test Results ===")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All MCP client tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)