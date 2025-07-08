# Nablax Agent Service - MCP 技术文档

## 1. MCP 实现简介

本服务通过实现 Model Context Protocol (MCP)，作为智能任务检测与工具编排的中间层，支持多种 AI 工具的统一调用与扩展。MCP 允许通过标准协议与下游 AI 服务（如邮件草稿生成、文档摘要等）进行通信，并支持智能任务类型检测与自动路由。

## 2. 架构与主要组件

- **FastAPI 服务**：对外提供统一的 HTTP API。
- **MCP Client**：如 `EmailDraftMCPClient`，负责与 MCP 服务器通信。
- **工具注册表**：`AVAILABLE_MCP_TOOLS`，集中管理所有可用 MCP 工具及其元数据。
- **任务检测逻辑**：根据输入内容和上下文智能判断所需工具。
- **Fallback 机制**：MCP 工具调用失败时自动切换到备用实现（如直连 Azure OpenAI）。

## 3. 任务检测与工具选择流程

1. 接收请求（如 `/agent/do-task`）。
2. 提取输入数据，分析文本内容和上下文。
3. 通过关键词和上下文匹配，智能检测任务类型。
4. 根据任务类型，从注册表选择合适的 MCP 工具。
5. 调用对应的 MCP 客户端方法，返回结果。
6. 若主流程失败，自动切换到 fallback 实现。

## 4. 主要类和方法说明

### EmailDraftMCPClient
- 负责与 MCP 邮件草稿服务通信。
- 主要方法：
  - `generate_email_draft`：生成邮件草稿。
  - `get_email_templates`：获取邮件模板。
  - `get_best_practices`：获取邮件最佳实践。

### select_and_execute_mcp_tool
- 根据任务类型和输入数据，选择并执行合适的 MCP 工具。
- 内置 fallback 机制，保证高可用。

### detect_task_type
- 智能分析输入内容，自动判断所需工具类型。
- 支持关键词匹配和上下文分析。

## 5. 扩展 MCP 工具的步骤

1. 实现新的 MCP 客户端类（如 `DocumentSummaryMCPClient`）。
2. 在 `AVAILABLE_MCP_TOOLS` 注册新工具，配置 client、method、描述和关键词。
3. 在 `select_and_execute_mcp_tool` 中添加新工具的参数处理与调用逻辑。
4. （可选）实现 fallback 备用方案。

## 6. 典型调用流程示例

1. 客户端调用 `/agent/do-task`，传入原始邮件和上下文：
   ```json
   {
     "input_data": {
       "original_mail": "Hi, can you send me the report?",
       "context": {"reply_type": "reply", "tone": "friendly"}
     }
   }
   ```
2. 服务自动检测为邮件草稿任务，调用 `EmailDraftMCPClient.generate_email_draft`。
3. 若 MCP 服务异常，自动切换到 Azure OpenAI 直连实现。
4. 返回生成的邮件草稿。

## 7. 注意事项与最佳实践

- MCP 工具需实现标准接口，便于统一编排。
- 工具注册表中的关键词应覆盖常见表达，提升任务检测准确率。
- 推荐为每个工具实现 fallback 方案，提升系统鲁棒性。
- 新增工具时，需同步完善注册表和参数处理逻辑。
- 日志与异常处理应完善，便于排查问题。

---
如需进一步扩展或集成新 AI 工具，请参考本文件第 5 节的步骤。
