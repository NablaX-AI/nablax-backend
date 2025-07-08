# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **MCP-compliant three-tier email reply service** based on FastAPI with microservices architecture. The system uses the **Model Context Protocol (MCP)** standard to provide intelligent email response generation through Azure OpenAI, following Anthropic's MCP specification.

## Architecture

### MCP-Based Three-Tier Structure

```
[Client]
   ↓ POST /do-task (generic) or /generate-reply (legacy)
[FastAPI Gateway Service] (Port 8000 - External Entry)
   ↓ POST /agent/do-task
[Agent Service] (Port 8001 - Intent Detection & MCP Orchestration)
   ↓ MCP Client calls MCP Server via stdio
[MCP Server] (stdio subprocess - LLM + Tools + Resources)
   ↓ Azure OpenAI API calls
[Azure OpenAI] → [MCP Response] → [Agent Processing] → [FastAPI] → [Client]
```

### Service Responsibilities

1. **FastAPI Gateway Service** (`services/fastapi_service/`)
   - External API gateway on port 8000
   - Generic endpoint: `POST /do-task` (automatic intent detection)
   - Legacy endpoint: `POST /generate-reply` (backward compatibility)
   - System capabilities and debug endpoints

2. **Agent Service** (`services/agent_service/`)
   - Intent detection and task orchestration on port 8001
   - MCP Client integration for calling MCP servers
   - Endpoint: `POST /agent/do-task` (generic task processing)
   - Fallback handling and response validation

3. **MCP Server** (`services/mail_draft_mcp_service/`)
   - Compliant MCP Server implementation (stdio protocol)
   - Tools: `generate_email_draft`
   - Resources: `email_templates`, `best_practices`
   - Direct Azure OpenAI integration with structured prompts

## Model Context Protocol (MCP) Implementation

### MCP Server Features
- **Tools**: Email draft generation with configurable tone and style
- **Resources**: Email templates and best practices
- **Prompts**: Structured email generation prompts
- **Protocol**: MCP 2024-11-05 specification compliant

### MCP Client Integration
- Agent service acts as MCP Client
- Communicates with MCP Server via stdio/subprocess
- Automatic server lifecycle management
- Error handling and fallback responses

## Development Setup

### Environment Configuration
```bash
# Copy and configure Azure OpenAI settings
cp .env.example .env
# Edit .env to add your Azure OpenAI configuration:
# AZURE_OPENAI_API_KEY="your_key"
# AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
# AZURE_OPENAI_MODEL="gpt-4"
# AZURE_OPENAI_API_VERSION="2024-12-01-preview"
```

### Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Using uv (recommended)
uv pip install -r requirements.txt
```

### Running Services

#### MCP-Based Development Mode
```bash
# Start all MCP services
./scripts/start_mcp_services.sh

# Stop all services
./scripts/stop_mcp_services.sh

# View logs
tail -f logs/*.log
```

#### Individual Services
```bash
# Start Agent service (includes MCP client)
cd services/agent_service && PYTHONPATH="../../:$PYTHONPATH" python -m uvicorn main:app --reload --port 8001

# Start FastAPI gateway
cd services/fastapi_service && PYTHONPATH="../../:$PYTHONPATH" python -m uvicorn main:app --reload --port 8000

# Test MCP server directly (debug only)
cd services/mail_draft_mcp_service && python mcp_server.py
```

### Testing
```bash
# Test complete MCP flow
python test_mcp_flow.py

# Test individual endpoints
curl -X POST http://localhost:8000/do-task \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"original_mail": "Test email content", "context": {}}}'

# Get system capabilities
curl http://localhost:8000/capabilities

# Debug MCP flow
curl http://localhost:8000/debug/mcp-flow
```

## API Endpoints

### FastAPI Gateway Service (Port 8000)
- `GET /` - Service info with MCP architecture details
- `GET /health` - Health check with MCP status
- `POST /do-task` - **Generic task processing** (auto intent detection)
- `POST /generate-reply` - Legacy email generation (backward compatibility)
- `GET /capabilities` - System capabilities and MCP tools
- `GET /debug/mcp-flow` - MCP architecture debug information

### Agent Service (Port 8001)
- `GET /` - Service info
- `GET /health` - Health check with MCP protocol info
- `POST /agent/do-task` - Generic task processing with MCP orchestration
- `POST /agent/mail_draft` - Legacy email draft endpoint
- `GET /agent/tools` - Available MCP tools and capabilities
- `GET /agent/resources` - MCP resources (templates, best practices)

### MCP Server (stdio)
- **Tools**: `generate_email_draft`
- **Resources**: `email://templates`, `email://best_practices`
- **Protocol**: MCP 2024-11-05 via stdio communication

## Data Models

All services use unified response format:
```json
{
  "success": true,
  "data": {...},
  "error": null
}
```

Key schemas in `app/models/schemas.py`:
- `DoTaskRequest` - Generic task processing format
- `MailGenerateRequest` - Legacy email request format
- `AgentMailDraftRequest` - Agent service format
- `ApiResponse` - Unified response wrapper

## MCP Protocol Integration

### Client-Server Communication
- **Protocol**: MCP 2024-11-05 specification
- **Transport**: stdio (subprocess)
- **Client**: Agent service using MCP Python SDK
- **Server**: Dedicated MCP server with email tools

### Tool Execution Flow
1. Agent receives task request
2. Agent identifies intent (email_draft)
3. Agent creates MCP client session
4. Agent calls `generate_email_draft` tool via MCP
5. MCP server processes request with Azure OpenAI
6. MCP server returns structured JSON response
7. Agent validates and forwards response

## Error Handling & Resilience

- **MCP Fallbacks**: Each service provides fallback responses on MCP errors
- **Timeout Handling**: 45-60 second timeouts with graceful degradation
- **Azure OpenAI Errors**: Automatic fallback responses on API failures
- **Service Dependencies**: Agent depends on MCP server availability
- **Health Checks**: All services expose health endpoints
- **Protocol Compliance**: Strict MCP protocol adherence with error recovery

## File Structure

```
├── app/
│   └── models/schemas.py           # Pydantic data models
├── services/
│   ├── fastapi_service/main.py     # API gateway service
│   ├── agent_service/
│   │   ├── main.py                 # Agent orchestration service
│   │   └── mcp_client.py           # MCP client implementation
│   └── mail_draft_mcp_service/
│       └── mcp_server.py           # MCP server implementation
├── scripts/
│   ├── start_mcp_services.sh       # MCP services startup
│   └── stop_mcp_services.sh        # Service shutdown
├── test_mcp_flow.py                # Comprehensive MCP testing
├── requirements.txt                # Dependencies (includes mcp SDK)
└── .env.example                    # Azure OpenAI configuration template
```

## Configuration

### Environment Variables
- `AZURE_OPENAI_API_KEY` - Required for MCP server
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI resource endpoint
- `AZURE_OPENAI_MODEL` - Model deployment name (e.g., "gpt-4")
- `AZURE_OPENAI_API_VERSION` - API version (e.g., "2024-12-01-preview")
- `AGENT_SERVICE_URL` - FastAPI service configuration

### Service URLs (Development)
- FastAPI Gateway: http://localhost:8000
- Agent Service: http://localhost:8001
- MCP Server: stdio subprocess (managed by Agent)

## MCP Protocol Compliance

- **Specification**: MCP 2024-11-05
- **SDK**: Official MCP Python SDK
- **Transport**: stdio for server communication
- **Tools**: Structured tool definitions with JSON schemas
- **Resources**: Email templates and best practices
- **Error Handling**: MCP-compliant error responses

## Monitoring & Debugging

- Service logs written to `logs/` directory
- MCP protocol debug endpoint: `/debug/mcp-flow`
- System capabilities endpoint: `/capabilities`
- Agent tools and resources: `/agent/tools`, `/agent/resources`
- Use `test_mcp_flow.py` for end-to-end MCP testing

## Future Enhancements

- Multiple MCP servers for different task types
- Enhanced intent detection with ML models
- MCP resource caching and optimization
- Advanced prompt template management
- Multi-model Azure OpenAI support

使用 uv + requirement 管理python 项目，

包装好 mcp 服务，并提供给 agent 使用。