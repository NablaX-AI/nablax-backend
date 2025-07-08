import os
from openai import AzureOpenAI
import base64
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量获取配置
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

deployment = os.getenv("AZURE_OPENAI_MODEL")


client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

根据上面代码，修改代码里的 llm call。

我已经设置好了 .env 文件，测试项目。


创建 git .ingnore。
update readme.md。