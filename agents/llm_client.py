from typing import Any, Dict, List
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 全局客户端实例
_client = None

def get_llm_client():
    """Get or create the Azure OpenAI client."""
    global _client
    if _client is None:
        # 从环境变量获取配置
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
        
        _client = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=endpoint,
            api_key=subscription_key,
        )
    return _client

async def call_llm(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> str:
    """
    General function to call Azure OpenAI LLM.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        temperature: Temperature parameter for the model
        max_tokens: Maximum number of tokens to generate
    
    Returns:
        Generated text content
    
    Raises:
        Exception: If the LLM call fails
    """
    client = get_llm_client()
    deployment = os.getenv("AZURE_OPENAI_MODEL", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))
    
    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content