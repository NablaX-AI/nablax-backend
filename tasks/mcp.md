Model Context Protocol (MCP) 是由 Anthropic 推出的开放标准，旨在为大型语言模型（LLM）提供统一的上下文和工具访问接口。通过 MCP，LLM 可以安全、标准化地连接到外部数据源和功能模块。([zh.wikipedia.org][1], [github.com][2])

---

## 🧱 MCP 架构概览

* **MCP 服务器**：提供数据（资源）、功能（工具）和提示（提示模板）的服务端。
* **MCP 客户端**：通常是 LLM 应用程序，连接到 MCP 服务器以获取上下文或执行操作。([github.com][3])

MCP 客户端和服务器通常是 Python 程序，但也可以使用其他语言实现。例如，Gradio 提供了将其聊天界面作为 MCP 客户端的示例。([gradio.app][4])

---

## 🛠 如何构建 MCP 服务器

1. **安装 MCP Python SDK**：

   ```bash
   pip install mcp
   ```



2. **创建资源、工具和提示**：

   ```python
   from mcp import Resource, Tool, Prompt

   # 资源示例：提供用户信息
   user_info = Resource(name="user_info", data={"name": "Alice", "age": 30})

   # 工具示例：发送电子邮件草稿
   def send_email_draft(recipient, subject, body):
       # 实现发送邮件的逻辑
       pass

   email_tool = Tool(name="send_email_draft", function=send_email_draft)

   # 提示示例：生成电子邮件草稿的提示模板
   email_prompt = Prompt(name="email_draft", template="请为 {recipient} 撰写一封关于 {subject} 的电子邮件。")
   ```



3. **启动 MCP 服务器**：

   ```python
   from mcp import Server

   server = Server(resources=[user_info], tools=[email_tool], prompts=[email_prompt])
   server.start()
   ```



上述代码展示了如何使用 MCP Python SDK 创建一个简单的服务器，提供用户信息资源、发送电子邮件的工具和生成电子邮件草稿的提示模板。

---

## 🤖 如何构建支持 MCP 的聊天机器人

1. **安装 MCP 客户端 SDK**：

   ```bash
   pip install mcp
   ```



2. **连接到 MCP 服务器**：

   ```python
   from mcp import Client

   client = Client(server_url="http://localhost:5000")
   ```



3. **使用 MCP 工具**：

   ```python
   response = client.call_tool("send_email_draft", recipient="Bob", subject="会议安排", body="请安排明天的会议。")
   ```



通过上述步骤，聊天机器人可以通过 MCP 客户端调用服务器提供的工具，如发送电子邮件草稿。

---

## 📍 关于 `email_draft` 的调用位置

`email_draft` 函数作为 MCP 服务器提供的工具之一，通常在聊天机器人或其他客户端应用程序中被调用。当用户请求发送电子邮件草稿时，客户端会通过 MCP 协议调用服务器上的 `send_email_draft` 工具。服务器接收到请求后，执行相应的函数，并将结果返回给客户端。

---
