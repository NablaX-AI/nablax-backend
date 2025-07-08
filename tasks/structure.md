你现在的目标是：**定义后端系统的服务结构**，包括 FastAPI、agent 服务、mcp 服务（比如mail_draft_mcp） 三部分，并以 MCP 协议为智能服务标准。

---

# 🌐 通用后端服务分层架构（以邮件草稿回复为例，基于 MCP 协议）

## 1. 总体分层结构

```
[Client]
   ↓ 提交原始输入（无需指定任务类型）
[API Gateway / FastAPI]
   ↓ 转发请求
[Agent Service]
   ↓ 意图识别 + 任务分发/编排
[LLM/Tool Service（如 mail_draft_mcp，基于 MCP 协议）]
   ↓ 返回结构化结果
[Agent 整理]
   ↓
[API Gateway 响应]
   ↓
[Client 展示结果]
```

---

## 2. 各层职责通用描述

### 1. API Gateway / FastAPI（对外入口）

- 统一对外暴露 RESTful API（如 POST /do-task）
- 接收用户原始输入（如：文本、邮件内容、附件等）
- 转发请求到 Agent 层
- 负责统一响应格式、异常处理、权限校验等
- 示例（邮件草稿回复）：
  - 接收原始邮件和上下文，转发给 Agent

### 2. Agent Service（中间协调/意图识别/编排）

- 负责意图识别（如：分类、NLU、prompt 解析等）
- 根据识别结果分发到对应下游服务
- 可实现多种业务逻辑、格式校验、fallback、重试等
- 统一对接下游智能服务（如 LLM、工具服务），推荐通过 MCP 协议调用
- 示例（邮件草稿回复）：
  - 识别为邮件回复任务，整理 prompt，调用 mail_draft_mcp（MCP 工具），校验 LLM 返回格式

### 3. 智能/工具服务（如 mail_draft_mcp，MCP 服务器）

- 封装具体的智能能力（如 LLM、外部 API、算法等），并通过 MCP 协议对外暴露
- 输入为结构化请求，输出为结构化结果（如 JSON）
- 可根据不同任务类型扩展不同 MCP 工具
- 示例（邮件草稿回复）：
  - 输入邮件内容和指令，输出邮件回复草稿 JSON
- 推荐实现方式：参考 MCP Python SDK，定义 Resource、Tool、Prompt，并启动 MCP Server

---

## 3. 通用数据流与接口调用（MCP 标准）

```plaintext
Client
 └── POST /do-task
      → body: { input_data, ... }  # 无需指定 task_type

API Gateway
 └── POST /agent/do-task
      → body: { input_data, ... }

Agent
 └── MCP Client 调用 MCP Server 工具
      → client.call_tool("tool_name", ...)

MCP Server (LLM/Tool Service)
 └── response: { result_data }

Agent → API Gateway → Client
```

- 以邮件草稿为例，Client 只需提交原始邮件内容，Agent 自动识别为邮件回复任务，通过 MCP 协议调用 mail_draft_mcp 工具。

---

## 4. 通用接口返回格式建议

```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

- 便于前后端统一处理、异常追踪和扩展。

---

## 5. 通用化建议

- Client 只需提交原始输入，极简调用体验。
- Agent 层负责意图识别和任务分发，便于后续扩展多种智能任务。
- 智能/工具服务推荐基于 MCP 协议实现，便于标准化和横向扩展（如：邮件草稿、摘要、翻译等）。
- 统一接口规范和错误处理，提升系统健壮性。

---

如需将该架构应用于其他智能任务（如文档摘要、自动回复、内容审核等），只需在 Agent 层扩展意图识别和分发逻辑，在 MCP Server 层扩展对应的 Tool 即可。

如需更详细的代码模板或具体实现建议，请告知！

---

# ✅ MCP 相关实现与邮件草稿服务示例

## 1. MCP 服务器（mail_draft_mcp）实现参考

```python
from mcp import Resource, Tool, Prompt, Server

def send_email_draft(recipient, subject, body):
    # 实现邮件草稿生成逻辑
    ...

email_tool = Tool(name="send_email_draft", function=send_email_draft)
email_prompt = Prompt(name="email_draft", template="请为 {recipient} 撰写一封关于 {subject} 的电子邮件。")

server = Server(resources=[], tools=[email_tool], prompts=[email_prompt])
server.start()
```

## 2. Agent 作为 MCP 客户端调用工具

```python
from mcp import Client

client = Client(server_url="http://mail-draft-mcp:5000")
response = client.call_tool("send_email_draft", recipient="Bob", subject="会议安排", body="请安排明天的会议。")
```

## 3. 数据流与接口调用关系（邮件草稿为例）

```plaintext
Client
 └── POST /generate-reply
      → body: {
            original_mail: "...",
            context: {...}
        }

FastAPI
 └── POST /agent/do-task
      → body: {
            input_data: {...}
        }

Agent
 └── MCP Client 调用 mail_draft_mcp 工具
      → client.call_tool("send_email_draft", ...)

mail_draft_mcp (MCP Server)
 └── response:
      {
        reply_subject: "...",
        reply_body: "..."
      }

Agent → FastAPI → Client
```

## 4. FastAPI 示例定义（伪代码）

```python
@app.post("/generate-reply")
async def generate_reply(request: MailRequest):
    # 调用 agent API
    agent_resp = requests.post("http://agent-service/agent/do-task", json=request.dict())
    draft = agent_resp.json()
    return {
        "reply_subject": draft["reply_subject"],
        "reply_body": beautify(draft["reply_body"])
    }
```

---

## 5. 接口稳定性与错误处理建议

* 所有接口建议返回结构统一：

```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

* MCP 服务可能 LLM timeout/格式异常，建议加 fallback 或 retry。
* Agent 可做格式验证、预处理、安全清洗等工作。

---

> 本架构已对齐 MCP 协议标准，推荐所有智能/工具服务均以 MCP 方式实现和调用，便于后续横向扩展和标准化管理。

使用 uv + requirement 管理python 项目，

包装好 mcp 服务，并提供给 agent 使用。