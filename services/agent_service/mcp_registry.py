"""
MCP Registry System - Manages MCP servers based on configuration file
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass

from .mcp_client import MCPClient

logger = logging.getLogger(__name__)

@dataclass
class MCPServerInfo:
    """MCP Server Information"""
    name: str
    command: str
    args: List[str]
    description: str = ""
    keywords: List[str] = None
    client: Optional[MCPClient] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

class MCPRegistry:
    """
    MCP Registry manages MCP servers based on configuration file.
    Supports external MCP servers with custom commands and arguments.
    """
    
    def __init__(self, config_file: str = None):
        """Initialize MCP registry with configuration file."""
        self.config_file = config_file or self._get_default_config_file()
        self.servers: Dict[str, MCPServerInfo] = {}
        self.load_config()
    
    def _get_default_config_file(self) -> str:
        """Get default config file path."""
        return os.path.join(os.path.dirname(__file__), "mcp.config")
    
    def load_config(self) -> None:
        """Load MCP servers from configuration file."""
        try:
            if not os.path.exists(self.config_file):
                logger.warning(f"⚠️  MCP config file not found: {self.config_file}")
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            mcp_servers = config.get('mcpServers', {})
            
            for server_name, server_config in mcp_servers.items():
                # Extract server info
                command = server_config.get('command', 'python')
                args = server_config.get('args', [])
                description = server_config.get('description', f"MCP Server: {server_name}")
                keywords = server_config.get('keywords', [])
                
                # Create server info
                server_info = MCPServerInfo(
                    name=server_name,
                    command=command,
                    args=args,
                    description=description,
                    keywords=keywords
                )
                
                # Create MCP client for this server
                server_info.client = MCPClient(
                    server_command=command,
                    server_args=args,
                    timeout=30
                )
                
                self.servers[server_name] = server_info
                logger.info(f"✅ Registered MCP server: {server_name}")
            
            logger.info(f"📋 Loaded {len(self.servers)} MCP servers from config")
            
        except Exception as e:
            logger.error(f"❌ Failed to load MCP config: {e}")
    
    def get_server(self, name: str) -> Optional[MCPServerInfo]:
        """Get MCP server by name."""
        return self.servers.get(name)
    
    def get_all_servers(self) -> Dict[str, MCPServerInfo]:
        """Get all registered MCP servers."""
        return self.servers.copy()
    
    def find_server_by_keywords(self, text: str) -> Optional[MCPServerInfo]:
        """Find MCP server by keyword matching."""
        text_lower = text.lower()
        
        for server in self.servers.values():
            for keyword in server.keywords:
                if keyword.lower() in text_lower:
                    return server
        
        # Fallback: check server name
        for server_name, server in self.servers.items():
            if server_name.lower() in text_lower:
                return server
        
        return None
    
    def list_servers(self) -> List[Dict[str, Any]]:
        """List all registered servers."""
        return [
            {
                "name": server.name,
                "command": server.command,
                "args": server.args,
                "description": server.description,
                "keywords": server.keywords
            }
            for server in self.servers.values()
        ]
    
    async def get_server_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """Get tools available on a specific server."""
        server = self.get_server(server_name)
        if not server or not server.client:
            return []
        
        try:
            async with server.client as client:
                tools = await client.list_tools()
                return tools
        except Exception as e:
            logger.error(f"❌ Failed to get tools from {server_name}: {e}")
            return []
    
    async def call_server_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on a specific server."""
        server = self.get_server(server_name)
        if not server or not server.client:
            raise ValueError(f"Server not found: {server_name}")
        
        try:
            async with server.client as client:
                result = await client.call_tool(tool_name, arguments)
                return result
        except Exception as e:
            logger.error(f"❌ Failed to call tool {tool_name} on {server_name}: {e}")
            raise
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        logger.info("🔄 Reloading MCP configuration...")
        self.servers.clear()
        self.load_config()


# Global registry instance
_registry = None

def get_mcp_registry() -> MCPRegistry:
    """Get global MCP registry instance."""
    global _registry
    if _registry is None:
        _registry = MCPRegistry()
    return _registry

def reload_mcp_config():
    """Reload MCP configuration."""
    global _registry
    if _registry:
        _registry.reload_config()

# Convenience functions
def get_server(name: str) -> Optional[MCPServerInfo]:
    """Get MCP server by name."""
    return get_mcp_registry().get_server(name)

def get_all_servers() -> Dict[str, MCPServerInfo]:
    """Get all registered MCP servers."""
    return get_mcp_registry().get_all_servers()

def find_server_by_keywords(text: str) -> Optional[MCPServerInfo]:
    """Find MCP server by keyword matching."""
    return get_mcp_registry().find_server_by_keywords(text)

def list_all_servers() -> List[Dict[str, Any]]:
    """List all registered servers."""
    return get_mcp_registry().list_servers()

async def get_server_tools(server_name: str) -> List[Dict[str, Any]]:
    """Get tools available on a specific server."""
    return await get_mcp_registry().get_server_tools(server_name)

async def call_server_tool(server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Call a tool on a specific server."""
    return await get_mcp_registry().call_server_tool(server_name, tool_name, arguments)


# CLI for testing
if __name__ == "__main__":
    import asyncio
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Registry Management")
    parser.add_argument("action", choices=["list", "tools", "test"])
    parser.add_argument("--server", help="Server name")
    parser.add_argument("--tool", help="Tool name")
    parser.add_argument("--args", help="Tool arguments (JSON)")
    
    args = parser.parse_args()
    
    async def main():
        registry = get_mcp_registry()
        
        if args.action == "list":
            servers = registry.list_servers()
            print(f"📋 Found {len(servers)} MCP servers:")
            for server in servers:
                print(f"  • {server['name']}")
                print(f"    Command: {server['command']} {' '.join(server['args'])}")
                print(f"    Description: {server['description']}")
                print(f"    Keywords: {', '.join(server['keywords'])}")
                print()
        
        elif args.action == "tools":
            if not args.server:
                print("❌ Server name required for tools command")
                return
            
            tools = await registry.get_server_tools(args.server)
            print(f"🔧 Tools available on {args.server}:")
            for tool in tools:
                name = tool.get('name', 'Unknown')
                desc = tool.get('description', 'No description')
                print(f"  • {name}: {desc}")
        
        elif args.action == "test":
            if not all([args.server, args.tool]):
                print("❌ Server name and tool name required for test command")
                return
            
            test_args = {}
            if args.args:
                try:
                    test_args = json.loads(args.args)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON for arguments")
                    return
            
            try:
                result = await registry.call_server_tool(args.server, args.tool, test_args)
                print(f"✅ Result from {args.server}.{args.tool}:")
                print(json.dumps(result, indent=2, default=str))
            except Exception as e:
                print(f"❌ Error: {e}")
    
    asyncio.run(main())