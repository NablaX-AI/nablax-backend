# Nablax Backend - 基于 MCP 的通用智能代理服务

## 项目简介

Nablax Backend 是一个基于 **Model Context Protocol (MCP)** 的通用智能代理服务，具备自动任务识别和处理能力。系统采用函数式架构设计，通过 MCP 协议集成多种工具，目前主要支持邮件草稿生成功能。

## 核心特性

- **🎯 智能任务识别**：自动检测任务类型（邮件处理、通用查询等）
- **🚀 统一 API 接口**：单一 `/do-task` 端点处理所有任务
- **🔧 MCP 工具生态**：基于 MCP 协议的可扩展工具系统
- **⚡ 函数式架构**：纯函数设计，避免不必要的类结构
- **📧 邮件处理专长**：智能邮件回复生成，支持多种语调

## 系统架构

```
[Client Request]
       ↓
[FastAPI Application] (Port 8000)
       ↓ 
[General Agent] (Task Detection & Processing)
       ↓
[MCP Server] (Tool Execution via stdio)
       ↓
[Azure OpenAI] (LLM Processing)
```

### 架构组件

| 组件             | 职责                           | 技术栈         |
|------------------|--------------------------------|----------------|
| FastAPI App      | 统一API网关，路由管理          | FastAPI        |
| General Agent    | 任务识别，智能处理             | Python Functions |
| MCP Server       | 工具执行，LLM集成              | MCP Protocol   |
| Azure OpenAI     | 自然语言处理                   | GPT-4          |

## 项目结构

```
nablax-backend/
├── main.py                         # FastAPI 应用入口
├── routes.py                       # 路由函数定义
├── schemas.py                      # 请求/响应数据模型
├── mcp.config                      # MCP服务器配置
├── api/
│   └── email_router.py             # 邮件相关API路由
├── agents/
│   ├── agent.py                    # 通用代理逻辑
│   ├── schema.py                   # 代理数据模型
│   ├── mcp_client.py               # MCP客户端
│   ├── llm_client.py               # LLM客户端
│   └── email_agent/                # 邮件专用工具
│       ├── agent.py                # 邮件处理逻辑
│       ├── utils.py                # 邮件工具函数
│       └── schema.py               # 邮件数据模型
├── mcp_server/
│   ├── README.md                   # MCP服务器目录说明
│   └── mail_draft_mcp/             # 邮件草稿MCP服务
├── tests/
└── requirements.txt
```

## 快速开始

### 1. 环境准备

```bash
cp .env.example .env
```

### 2. 安装依赖

```bash
# 使用 uv（推荐）
uv sync
```

### 3. 启动服务

```bash
source .venv/bin/activate
uv run main.py
```

### 4. 测试服务

```bash
# 测试健康状态
curl http://localhost:8000/health

# 测试邮件回复功能
curl -X POST http://localhost:8000/do-task \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "user_request": "help me reply to this email: Hello, I hope you are doing well. Could we schedule a meeting next week?"
    }
  }'

# 运行完整测试
python test_refactored.py
python test_email_functionality.py
```

## API 接口

### 核心接口

#### POST /do-task
通用任务处理接口，支持自动任务识别。

**请求格式**：
```json
{
  "input_data": {
    "user_request": "help me reply to this email: [邮件内容]",
    "context": {
      "type": "optional_context"
    }
  }
}
```

**支持的任务类型**：
1. **邮件处理** - 包含关键词：email, mail, reply, draft, 邮件, 回复
2. **通用查询** - 其他类型的请求

**响应格式**：
```json
{
  "success": true,
  "task_type": "email_draft",
  "detected_tone": "professional",
  "extracted_content": "Hello, I hope you are doing well...",
  "data": {
    "reply_subject": "Re: Your email",
    "reply_body": "Generated email content..."
  }
}
```

### 其他接口

- `GET /health` - 健康检查
- `GET /capabilities` - 系统能力查询
- `GET /debug/mcp-flow` - MCP架构调试信息
- `POST /email/do-task` - 邮件专用接口
- `GET /agent/servers` - MCP服务器列表

## 功能特性

### 智能任务识别

系统自动分析用户请求，识别任务类型：

```python
# 邮件任务示例
"help me reply to this email: Hello..."  → email_draft
"请帮我回复邮件：您好..."              → email_draft

# 语调检测
"紧急：help me reply..."              → urgent tone
"轻松地回复这封邮件..."               → casual tone
```

### 邮件处理能力

- **智能内容提取**：从用户请求中提取原始邮件内容
- **语调检测**：自动识别并生成合适语调的回复
  - Professional（专业）
  - Casual（轻松）
  - Urgent（紧急）
  - Formal（正式）
  - Friendly（友好）
- **上下文理解**：基于邮件内容生成相关性强的回复

### MCP 集成

- **协议标准**：遵循 MCP 2024-11-05 规范
- **通信方式**：stdio 协议，进程间通信
- **工具发现**：自动发现和注册MCP工具
- **错误处理**：完善的降级和错误恢复机制

## 开发指南

### 函数式设计原则

项目采用函数式设计，避免不必要的类：

```python
# ✅ 推荐：使用函数
async def process_task(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理任务的纯函数"""
    pass

# ❌ 避免：不必要的类
class TaskProcessor:
    def process(self, input_data):
        pass
```

### 添加新任务类型

1. **更新任务检测逻辑**：
```python
# agents/agent.py
def detect_task_type(user_request: str) -> str:
    # 添加新的关键词检测
    if "翻译" in user_request.lower():
        return "translation"
```

2. **实现处理函数**：
```python
async def handle_translation_task(user_request: str, context: Dict[str, Any]):
    # 实现翻译逻辑
    pass
```

3. **注册到路由**：
```python
# routes.py 或 agents/agent.py
if task_type == "translation":
    return await handle_translation_task(user_request, context)
```

### 添加新 MCP 工具

1. **创建 MCP 服务器**：
```bash
mkdir -p mcp_server/my_new_tool
```

2. **实现工具逻辑**：
```python
# mcp_server/my_new_tool/server.py
# 参考 mail_draft_mcp 实现
```

3. **更新配置**：
```json
// mcp.config
{
  "mcpServers": {
    "my_new_tool": {
      "command": "python",
      "args": ["mcp_server/my_new_tool/server.py"],
      "keywords": ["关键词1", "关键词2"]
    }
  }
}
```

## 测试

### 运行测试

```bash
# 完整功能测试
python test_refactored.py

# 邮件功能专项测试
python test_email_functionality.py

# 单独测试组件
python -m pytest tests/
```

### 测试覆盖

- ✅ 基础导入和结构测试
- ✅ API路由功能测试
- ✅ 通用代理任务处理
- ✅ 邮件草稿生成功能
- ✅ MCP服务器集成测试
- ✅ 函数式架构验证

## 配置

### 环境变量

```env
# Azure OpenAI 配置（必需）
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-4
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### MCP 服务器配置

`mcp.config` 文件配置MCP服务器：

```json
{
  "mcpServers": {
    "mail_draft_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp_server/mail_draft_mcp",
        "run",
        "drafter.py"
      ],
      "description": "Generate email drafts and replies",
      "keywords": ["email", "mail", "draft", "reply", "邮件", "回复"]
    }
  }
}
```

## 监控与运维

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/health

# 查看系统能力
curl http://localhost:8000/capabilities

# 调试MCP流程
curl http://localhost:8000/debug/mcp-flow
```

### 日志

- **应用日志**：console 输出，包含任务处理流程
- **MCP日志**：MCP服务器通信日志
- **错误日志**：异常和错误处理日志

## 常见问题

### 邮件处理问题

1. **任务识别错误**：
   - 确保请求包含邮件相关关键词
   - 检查 `user_request` 格式是否正确

2. **MCP服务器连接失败**：
   - 检查 `mcp.config` 中的路径配置
   - 确认MCP服务器依赖已安装

3. **Azure OpenAI配置**：
   - 验证 `.env` 文件中的API密钥
   - 检查网络连接和权限

### 开发问题

1. **函数导入错误**：
   - 确保Python路径正确
   - 检查模块结构和导入语句

2. **测试失败**：
   - 运行 `python test_refactored.py` 检查基础功能
   - 查看具体错误日志进行调试

## 技术支持

### 文档资源

- [CLAUDE.md](CLAUDE.md) - 详细技术文档
- [API文档](http://localhost:8000/docs) - 启动服务后访问 
- [MCP协议文档](https://modelcontextprotocol.io/)

### 开发工具

- **uv**：Python包管理和虚拟环境
- **FastAPI**：高性能Web框架
- **MCP SDK**：Model Context Protocol Python SDK

---

## 项目信息

- **当前版本**：v2.0.0
- **Python版本**：>=3.10
- **MCP版本**：兼容 MCP 2024-11-05
- **维护状态**：积极维护中

## 未来规划

- 🔧 支持更多任务类型（文档总结、代码生成等）
- 🤖 改进任务识别算法
- 🔄 支持任务链和工作流
- 📊 添加监控和分析功能
- 🚀 云原生部署支持
- 🌐 多语言支持扩展