"""
LLM-based tool selection and argument generation for MCP agent service.
Uses Azure OpenAI to intelligently select tools and generate appropriate arguments.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from .llm_client import call_llm

logger = logging.getLogger(__name__)


class LLMToolSelector:
    """
    LLM-based tool selector that uses Azure OpenAI to intelligently 
    select appropriate tools and generate arguments.
    """
    
    def __init__(self, available_tools: Dict[str, Any]):
        """
        Initialize the LLM tool selector.
        
        Args:
            available_tools: Dictionary of available MCP tools with their info
        """
        self.available_tools = available_tools
    
    async def select_tool_and_generate_args(self, input_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Use LLM to select the most appropriate tool and generate arguments.
        
        Args:
            input_data: Input data from the user request
            
        Returns:
            Tuple of (tool_name, generated_arguments)
        """
        # Step 1: Get tool schemas from MCP clients
        logger.info("🔍 Getting tool schemas from MCP servers...")
        tool_schemas = await self._get_tool_schemas()
        
        # Log available tools
        logger.info(f"📋 Available tools from MCP servers:")
        for tool_name, schema in tool_schemas.items():
            logger.info(f"  - {tool_name}: {schema.get('description', 'No description')}")
            logger.info(f"    Method: {schema.get('name', 'Unknown')}")
            logger.info(f"    Keywords: {schema.get('keywords', [])}")
        
        # Step 2: Use LLM to select tool and generate arguments
        logger.info("🤖 Using LLM to select tool and generate arguments...")
        tool_name, arguments = await self._llm_select_and_generate(input_data, tool_schemas)
        
        logger.info(f"✅ LLM selected tool: {tool_name}")
        logger.info(f"✅ Generated arguments: {arguments}")
        
        return tool_name, arguments
    
    async def _get_tool_schemas(self) -> Dict[str, Any]:
        """
        Get tool schemas from available MCP tools.
        
        Returns:
            Dictionary of tool schemas with descriptions and input parameters
        """
        tool_schemas = {}
        
        for tool_name, tool_info in self.available_tools.items():
            try:
                # Get tool schema from MCP client
                client = tool_info["client"]
                
                # Use async context manager to get tools
                async with client as mcp_session:
                    tools = await mcp_session.list_tools()
                    logger.info(f"📡 MCP server returned {len(tools)} tools for {tool_name}")
                    
                    # Log all tools returned by MCP server
                    for i, tool in enumerate(tools):
                        tool_name_attr = getattr(tool, 'name', tool.get('name', 'Unknown')) if hasattr(tool, 'name') or isinstance(tool, dict) else 'Unknown'
                        tool_desc = getattr(tool, 'description', tool.get('description', 'No description')) if hasattr(tool, 'description') or isinstance(tool, dict) else 'No description'
                        logger.info(f"  Tool {i+1}: {tool_name_attr} - {tool_desc}")
                    
                    # Find the relevant tool
                    for tool in tools:
                        if hasattr(tool, 'name') and tool.name == tool_info["method"]:
                            tool_schemas[tool_name] = {
                                "name": tool.name,
                                "description": tool.description,
                                "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                                "keywords": tool_info.get("keywords", []),
                                "human_description": tool_info.get("description", "")
                            }
                            break
                        elif isinstance(tool, dict) and tool.get("name") == tool_info["method"]:
                            tool_schemas[tool_name] = {
                                "name": tool["name"],
                                "description": tool.get("description", ""),
                                "input_schema": tool.get("inputSchema", {}),
                                "keywords": tool_info.get("keywords", []),
                                "human_description": tool_info.get("description", "")
                            }
                            break
                    
                    # If no specific tool found, use the general info
                    if tool_name not in tool_schemas:
                        tool_schemas[tool_name] = {
                            "name": tool_info["method"],
                            "description": tool_info.get("description", ""),
                            "input_schema": self._get_default_schema(tool_name),
                            "keywords": tool_info.get("keywords", []),
                            "human_description": tool_info.get("description", "")
                        }
                        
            except Exception as e:
                logger.warning(f"Could not get schema for tool {tool_name}: {e}")
                # Use fallback schema
                tool_schemas[tool_name] = {
                    "name": tool_info["method"],
                    "description": tool_info.get("description", ""),
                    "input_schema": self._get_default_schema(tool_name),
                    "keywords": tool_info.get("keywords", []),
                    "human_description": tool_info.get("description", "")
                }
        
        return tool_schemas
    
    def _get_default_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get default schema for known tools."""
        if tool_name == "email_draft":
            return {
                "type": "object",
                "properties": {
                    "original_email": {
                        "type": "string",
                        "description": "The original email content to respond to"
                    },
                    "tone": {
                        "type": "string",
                        "description": "Tone of the reply (professional, casual, urgent)",
                        "enum": ["professional", "casual", "urgent"],
                        "default": "professional"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for email generation",
                        "properties": {
                            "reply_type": {"type": "string", "default": "reply"},
                            "urgency": {"type": "string", "default": "normal"},
                            "subject": {"type": "string"},
                            "sender_name": {"type": "string"}
                        }
                    }
                },
                "required": ["original_email"]
            }
        
        # Generic schema for unknown tools
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "string",
                    "description": "General input for the tool"
                }
            },
            "required": ["input"]
        }
    
    async def _llm_select_and_generate(self, input_data: Dict[str, Any], tool_schemas: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        Use LLM to select the best tool and generate arguments.
        
        Args:
            input_data: User input data
            tool_schemas: Available tool schemas
            
        Returns:
            Tuple of (selected_tool_name, generated_arguments)
        """
        # Create system prompt
        system_prompt = self._create_system_prompt(tool_schemas)
        
        # Create user prompt
        user_prompt = self._create_user_prompt(input_data)
        
        # Call LLM
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await call_llm(messages, temperature=0.3, max_tokens=1000)
            
            logger.info(f"🤖 LLM response: {response}")
            
            # Parse LLM response
            tool_name, arguments = self._parse_llm_response(response)
            
            # Validate the selection
            if tool_name not in self.available_tools:
                logger.warning(f"LLM selected unknown tool: {tool_name}, falling back to email_draft")
                tool_name = "email_draft"
                arguments = self._generate_fallback_arguments(input_data)
            
            return tool_name, arguments
            
        except Exception as e:
            logger.error(f"LLM tool selection failed: {e}")
            # Fallback to simple selection
            return self._fallback_selection(input_data)
    
    def _create_system_prompt(self, tool_schemas: Dict[str, Any]) -> str:
        """Create system prompt for LLM tool selection."""
        tools_description = []
        for tool_name, schema in tool_schemas.items():
            tools_description.append(
                f"Tool: {tool_name}\n"
                f"Description: {schema['description']}\n"
                f"Human Description: {schema['human_description']}\n"
                f"Keywords: {', '.join(schema['keywords'])}\n"
                f"Input Schema: {json.dumps(schema['input_schema'], indent=2)}\n"
            )
        
        return f"""你是一个智能工具选择助手，需要根据用户输入选择最合适的工具并生成相应的参数。

可用工具：
{chr(10).join(tools_description)}

请根据用户的输入：
1. 分析用户的需求和意图
2. 选择最合适的工具
3. 根据工具的输入模式生成正确的参数

响应格式必须是JSON：
{{
    "selected_tool": "tool_name",
    "reasoning": "选择原因的简短说明",
    "arguments": {{
        "parameter1": "value1",
        "parameter2": "value2"
    }}
}}

规则：
- 如果用户提到邮件、回复、草稿等，选择 email_draft 工具
- 仔细分析用户输入中的上下文信息
- 生成的参数必须符合工具的输入模式
- 如果不确定，优先选择 email_draft 工具"""
    
    def _create_user_prompt(self, input_data: Dict[str, Any]) -> str:
        """Create user prompt for tool selection."""
        # Handle natural language input
        if "user_request" in input_data:
            user_request = input_data["user_request"]
            return f"""用户自然语言请求：
"{user_request}"

请分析这个自然语言请求，识别用户的意图：
1. 如果用户要求回复邮件、写邮件、邮件草稿等，选择 email_draft 工具
2. 从用户请求中提取原始邮件内容
3. 根据用户的语气要求确定 tone（专业=professional，轻松=casual，紧急=urgent）
4. 生成符合工具要求的参数

原始输入数据：
{json.dumps(input_data, ensure_ascii=False, indent=2)}
"""
        else:
            # Legacy format support
            return f"""用户输入数据：
{json.dumps(input_data, ensure_ascii=False, indent=2)}

请分析这个输入，选择最合适的工具并生成相应的参数。"""
    
    def _parse_llm_response(self, response: str) -> Tuple[str, Dict[str, Any]]:
        """Parse LLM response to extract tool name and arguments."""
        try:
            # Try to parse as JSON
            parsed = json.loads(response.strip())
            
            tool_name = parsed.get("selected_tool", "email_draft")
            arguments = parsed.get("arguments", {})
            reasoning = parsed.get("reasoning", "No reasoning provided")
            
            logger.info(f"🎯 LLM tool selection result:")
            logger.info(f"  Selected tool: {tool_name}")
            logger.info(f"  Reasoning: {reasoning}")
            logger.info(f"  Generated arguments: {arguments}")
            
            return tool_name, arguments
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response was: {response}")
            
            # Try to extract tool name from text
            response_lower = response.lower()
            for tool_name in self.available_tools.keys():
                if tool_name in response_lower:
                    return tool_name, self._generate_fallback_arguments({"response": response})
            
            # Ultimate fallback
            return "email_draft", self._generate_fallback_arguments({"response": response})
    
    def _generate_fallback_arguments(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback arguments when LLM fails."""
        # Handle natural language input
        if "user_request" in input_data:
            user_request = input_data["user_request"]
            
            # Simple extraction of email content after common patterns
            original_email = user_request
            patterns = ["：", ":", "邮件", "内容是", "下面的"]
            for pattern in patterns:
                if pattern in user_request:
                    parts = user_request.split(pattern)
                    if len(parts) > 1:
                        original_email = parts[-1].strip()
                        break
            
            # Simple tone detection
            tone = "professional"
            if "轻松" in user_request or "casual" in user_request.lower():
                tone = "casual"
            elif "紧急" in user_request or "urgent" in user_request.lower():
                tone = "urgent"
            
            return {
                "original_email": original_email or "User request",
                "tone": tone,
                "context": {
                    "reply_type": "reply",
                    "urgency": "high" if tone == "urgent" else "normal"
                }
            }
        else:
            # Legacy format support
            text_content = ""
            for key, value in input_data.items():
                if isinstance(value, str):
                    text_content += value + " "
            
            return {
                "original_email": text_content.strip() or "User request",
                "tone": "professional",
                "context": {
                    "reply_type": "reply",
                    "urgency": "normal"
                }
            }
    
    def _fallback_selection(self, input_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Fallback tool selection when LLM fails."""
        logger.warning("Using fallback tool selection")
        
        # Simple keyword matching as fallback
        text_content = str(input_data).lower()
        
        # Check for email-related keywords
        email_keywords = ["email", "mail", "reply", "draft", "message", "respond"]
        if any(keyword in text_content for keyword in email_keywords):
            return "email_draft", self._generate_fallback_arguments(input_data)
        
        # Default to email_draft
        return "email_draft", self._generate_fallback_arguments(input_data)


# Factory function to create LLM tool selector
def create_llm_tool_selector(available_tools: Dict[str, Any]) -> LLMToolSelector:
    """Create LLM tool selector instance."""
    return LLMToolSelector(available_tools)