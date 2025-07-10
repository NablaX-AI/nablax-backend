# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
**Nablax Backend** is a **MCP-compliant email reply service** built with FastAPI and a function-based architecture. The system uses the **Model Context Protocol (MCP)** standard to provide intelligent email response generation through Azure OpenAI.


## Architecture

### Current Architecture (Single Service)
```
[Client] → [FastAPI App] → [General Agent] → [MCP Server] → [Azure OpenAI]
```

The system has been simplified from a three-tier microservices architecture to a single FastAPI service with intelligent task routing. The main components are:

1. **FastAPI Application** (`main.py`) - Single unified service on port 8000
2. **General Agent** (`agents/agent.py`) - Intelligent task detection and processing
3. **MCP Manager** (`agents/mcp_manager.py`) - MCP server orchestration and tool execution
4. **MCP Server** (`mcp_server/mail_draft_mcp/`) - Dedicated email processing server

## Key Commands

### Development Setup
```bash
# Install dependencies using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

### Running the Service
```bash
# Start the main service
python main.py
# OR
uv run main.py

# Service will be available at http://localhost:8000
```

### Testing
```bash
# Run unit tests
pytest tests/

# Test specific components
python tests/test_health_check.py
python tests/test_mcp_client.py
python tests/test_llm_client.py

# Test the complete flow
curl -X POST http://localhost:8000/do-task \
  -H "Content-Type: application/json" \
  -d '{"input_data": {"user_request": "help me reply to this email: Hello, how are you?"}}'
```

## API Endpoints

### Primary Endpoints
- `GET /` - Service info and MCP server status
- `GET /health` - Health check with MCP server availability
- `POST /do-task` - **Universal task processor** with automatic intent detection
- `GET /capabilities` - System capabilities and available MCP tools
- `GET /debug/mcp-flow` - MCP architecture debugging

### Email-Specific Endpoints
- `POST /email/do-task` - Email-specific task processing
- `POST /email/generate-reply` - Direct email generation
- `GET /email/capabilities` - Email processing capabilities

### Agent/MCP Management
- `GET /agent/servers` - List all MCP servers
- `GET /agent/servers/{server}/tools` - Get tools from specific server
- `POST /agent/servers/{server}/tools/{tool}` - Direct tool execution
- `POST /agent/reload-config` - Reload MCP configuration

## Configuration

### Environment Variables (`.env`)
```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_MODEL=gpt-4
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### MCP Configuration (`mcp.config`)
Configure MCP servers that provide tools and capabilities:
```json
{
  "mcpServers": {
    "mail_draft_mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp_server/mail_draft_mcp", "run", "drafter.py"],
      "description": "Generate email drafts and replies",
      "keywords": ["email", "mail", "draft", "reply", "邮件", "回复"]
    }
  }
}
```

## Code Architecture

### Function-Based Design
The codebase follows a **function-based architecture** (avoid classes unless necessary for abstraction):

- **Route Functions** (`routes.py`) - FastAPI route definitions
- **Agent Functions** (`agents/agent.py`) - Task processing logic
- **MCP Manager** (`agents/mcp_manager.py`) - MCP server orchestration
- **Utility Functions** (`agents/email_utils.py`) - Email processing helpers

### Key Data Flow
1. **Request Processing** - FastAPI routes receive and validate requests
2. **Task Detection** - Agent analyzes user input and detects intent (email vs general)
3. **MCP Routing** - MCP manager routes tasks to appropriate servers based on keywords
4. **Tool Execution** - MCP servers execute tools (e.g., `generate_email_draft`)
5. **Response Assembly** - Agent processes results and returns formatted responses

### MCP Protocol Integration
- **Protocol**: MCP 2024-11-05 specification
- **Transport**: stdio (subprocess communication)
- **Client**: Agent service using MCP Python SDK  
- **Server**: Dedicated MCP server in `mcp_server/mail_draft_mcp/`

## File Structure

```
├── main.py                    # FastAPI application entry point
├── routes.py                  # Route function definitions
├── schemas.py                 # Pydantic models for requests/responses
├── mcp.config                 # MCP server configuration
├── pyproject.toml             # Project dependencies and configuration
├── requirements.txt           # Python dependencies
├── api/
│   └── email_router.py        # Email-specific API routes
├── agents/
│   ├── agent.py               # General agent logic and task processing
│   ├── mcp_manager.py         # MCP server orchestration
│   ├── mcp_client.py          # MCP client implementation
│   ├── llm_client.py          # Azure OpenAI client
│   └── email_utils.py         # Email processing utilities
├── mcp_server/
│   └── mail_draft_mcp/        # MCP server implementation
│       ├── drafter.py         # Main MCP server script
│       ├── llm_client.py      # Azure OpenAI integration
│       └── prompts.py         # Email generation prompts
└── tests/                     # Test files
    ├── test_health_check.py
    ├── test_mcp_client.py
    └── test_llm_client.py
```

## Development Guidelines

1. **Use `uv` for package management** - Modern Python package manager
2. **Prefer functions over classes** - Only use classes when abstraction is necessary
3. **Follow MCP protocol standards** - Ensure compatibility with MCP 2024-11-05
4. **Test files go in `tests/` directory** - Maintain organized test structure
5. **Environment variables in `.env`** - Never commit secrets to repository

## Error Handling & Resilience

- **MCP Fallbacks** - Graceful degradation when MCP servers are unavailable
- **Timeout Handling** - 30-60 second timeouts with proper error responses
- **Azure OpenAI Errors** - Automatic fallback responses on API failures
- **Health Checks** - All endpoints provide health status information
- **Protocol Compliance** - Strict MCP protocol adherence with error recovery

## Common Development Tasks

### Adding New MCP Servers
1. Create server implementation in `mcp_server/`
2. Add server configuration to `mcp.config`
3. Update keywords for task routing
4. Test server integration via `/agent/servers` endpoints

### Extending Agent Capabilities
1. Modify task detection logic in `agents/agent.py`
2. Add new tool calls via MCP manager
3. Update response formatting as needed
4. Add corresponding tests in `tests/`

### Testing MCP Integration
```bash
# Get available servers
curl http://localhost:8000/agent/servers

# Test specific tool
curl -X POST http://localhost:8000/agent/servers/mail_draft_mcp/tools/generate_email_draft \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"original_mail": "Test email", "tone": "professional"}}'
```