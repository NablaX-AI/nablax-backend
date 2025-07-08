"""
MCP Client implementation for agent service.
Provides a wrapper around the MCP Python SDK for seamless integration.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPClient:
    """
    MCP Client wrapper that provides async context manager support
    and convenient methods for tool execution.
    """
    
    def __init__(self, server_script_path: str = None, server_cmd: str = "python", server_command: str = None, server_args: List[str] = None, timeout: int = 30):
        """
        Initialize MCP Client.
        
        Args:
            server_script_path: Path to the MCP server script (legacy support)
            server_cmd: Command to run the server (legacy support)
            server_command: Command to run the server (new way)
            server_args: Arguments for the server command (new way)
            timeout: Timeout for operations in seconds
        """
        # Support both old and new initialization methods
        if server_command and server_args:
            # New way: use command and args directly
            self.server_params = StdioServerParameters(
                command=server_command,
                args=server_args,
                env=None,
            )
        elif server_script_path:
            # Legacy way: use script path
            self.server_params = StdioServerParameters(
                command=server_cmd,
                args=[server_script_path],
                env=None,
            )
        else:
            raise ValueError("Either (server_command, server_args) or server_script_path must be provided")
        
        self.timeout = timeout
        self.session = None
        self._client_ctx = None
        self._read = None
        self._write = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        try:
            self._client_ctx = stdio_client(self.server_params)
            self._read, self._write = await asyncio.wait_for(
                self._client_ctx.__aenter__(),
                timeout=self.timeout
            )
            
            self.session = ClientSession(self._read, self._write)
            await self.session.__aenter__()
            
            # Initialize the session
            await asyncio.wait_for(
                self.session.initialize(),
                timeout=self.timeout
            )
            
            logger.info("MCP Client session initialized successfully")
            return self
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            if self.session:
                await self.session.__aexit__(type(e), e, e.__traceback__)
            if self._client_ctx:
                await self._client_ctx.__aexit__(type(e), e, e.__traceback__)
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        try:
            if self.session:
                await self.session.__aexit__(exc_type, exc_val, exc_tb)
            if self._client_ctx:
                await self._client_ctx.__aexit__(exc_type, exc_val, exc_tb)
            logger.info("MCP Client session closed")
        except Exception as e:
            logger.error(f"Error closing MCP client: {e}")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from the MCP server."""
        if not self.session:
            raise RuntimeError("MCP session not initialized")
        
        try:
            tools_response = await asyncio.wait_for(
                self.session.list_tools(),
                timeout=self.timeout
            )
            return tools_response.tools
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool with arguments."""
        if not self.session:
            raise RuntimeError("MCP session not initialized")
        
        try:
            result = await asyncio.wait_for(
                self.session.call_tool(tool_name, arguments),
                timeout=self.timeout
            )
            return result
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources from the MCP server."""
        if not self.session:
            raise RuntimeError("MCP session not initialized")
        
        try:
            resources_response = await asyncio.wait_for(
                self.session.list_resources(),
                timeout=self.timeout
            )
            return resources_response.resources
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            raise
    
    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Read a specific resource."""
        if not self.session:
            raise RuntimeError("MCP session not initialized")
        
        try:
            result = await asyncio.wait_for(
                self.session.read_resource(resource_uri),
                timeout=self.timeout
            )
            return result
        except Exception as e:
            logger.error(f"Failed to read resource {resource_uri}: {e}")
            raise


class EmailMCPClient(MCPClient):
    """
    Specialized MCP client for email-related operations.
    Extends MCPClient with email-specific methods.
    """
    
    async def generate_email_draft(self, original_email: str, tone: str = "professional", 
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an email draft using the MCP server.
        
        Args:
            original_email: The original email content
            tone: Tone of the reply (professional, casual, urgent, etc.)
            context: Additional context for generation
            
        Returns:
            Dict containing the generated email draft
        """
        if context is None:
            context = {}
        
        arguments = {
            "original_email": original_email,
            "tone": tone,
            "context": context
        }
        
        try:
            result = await self.call_tool("generate_email_draft", arguments)
            
            # Debug: log the actual result structure
            logger.info(f"MCP call result type: {type(result)}")
            logger.info(f"MCP call result: {result}")
            
            # Return raw result without any parsing
            return {
                "success": True,
                "raw_mcp_result": str(result),
                "mcp_result_type": str(type(result)),
                "data": {
                    "reply_subject": "MCP Tool Response",
                    "reply_body": str(result)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate email draft: {e}")
            raise
    
    async def get_email_templates(self) -> Dict[str, Any]:
        """Get email templates from the MCP server."""
        try:
            return await self.read_resource("email://templates")
        except Exception as e:
            logger.error(f"Failed to get email templates: {e}")
            # Return empty templates as fallback
            return {
                "templates": [],
                "error": str(e)
            }
    
    async def get_best_practices(self) -> Dict[str, Any]:
        """Get email best practices from the MCP server."""
        try:
            return await self.read_resource("email://best_practices")
        except Exception as e:
            logger.error(f"Failed to get best practices: {e}")
            # Return empty practices as fallback
            return {
                "practices": [],
                "error": str(e)
            }


def create_mcp_client(server_script_path: str = None, client_type: str = "email", server_command: str = None, server_args: List[str] = None) -> MCPClient:
    """
    Factory function to create MCP clients.
    
    Args:
        server_script_path: Path to the MCP server script (legacy support)
        client_type: Type of client to create ("email" or "generic")
        server_command: Command to run the server (new way)
        server_args: Arguments for the server command (new way)
        
    Returns:
        MCPClient instance
    """
    if client_type == "email":
        if server_command and server_args:
            return EmailMCPClient(server_command=server_command, server_args=server_args)
        else:
            return EmailMCPClient(server_script_path=server_script_path)
    else:
        if server_command and server_args:
            return MCPClient(server_command=server_command, server_args=server_args)
        else:
            return MCPClient(server_script_path=server_script_path)


# Example usage for testing
async def test_mcp_client():
    """Test function to demonstrate MCP client usage."""
    import os
    
    # Example server script path
    server_script = os.path.join(
        os.path.dirname(__file__), 
        "../mail_draft_mcp_service/mcp_server.py"
    )
    
    async with create_mcp_client(server_script, "email") as client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[tool.get('name', 'Unknown') for tool in tools]}")
        
        # Generate email draft
        result = await client.generate_email_draft(
            original_email="Hello, I need help with my account.",
            tone="professional",
            context={"urgency": "normal"}
        )
        print(f"Generated draft: {result}")


if __name__ == "__main__":
    asyncio.run(test_mcp_client())