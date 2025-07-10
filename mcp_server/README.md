# MCP Server Directory

## Overview
This directory contains **independent MCP (Model Context Protocol) server implementations**. Each subdirectory represents a standalone MCP server project that can be executed independently to provide specific tools and capabilities.

## Architecture Philosophy

### Individual Server Projects
- Each MCP server is a **completely independent Python project**
- Servers have their own dependencies, configuration, and business logic
- No shared dependencies or tight coupling between servers
- Each server can be developed, tested, and deployed independently

### MCP Protocol Compliance
- All servers implement the **MCP 2024-11-05 specification**
- Communication via **stdio protocol** (subprocess)
- Standard tool definitions with JSON schemas
- Proper error handling and response formatting

## Current MCP Servers

### 1. `mail_draft_mcp/` - Email Draft Generation Server
- **Purpose**: Generate email drafts and replies using Azure OpenAI
- **Tools**: `generate_email_draft`
- **Resources**: Email templates, best practices
- **Dependencies**: Azure OpenAI SDK, MCP Python SDK
- **Configuration**: Individual `pyproject.toml` and environment variables

## Server Structure

Each MCP server project follows this structure:
```
server_name/
├── pyproject.toml          # Project dependencies and metadata
├── README.md               # Server-specific documentation
├── CLAUDE.md               # Development instructions
├── main_module.py          # Core server implementation
├── llm_client.py          # LLM integration (if applicable)
├── prompts.py             # Prompt templates (if applicable)
├── tasks/                 # Development tasks and notes
└── uv.lock                # Dependency lock file
```

## Development Guidelines

### Adding New MCP Servers

1. **Create Independent Project**
   ```bash
   mkdir mcp_server/my_new_server
   cd mcp_server/my_new_server
   ```

2. **Initialize Project**
   ```bash
   uv init
   uv add mcp
   # Add other dependencies as needed
   ```

3. **Implement MCP Server**
   - Follow MCP 2024-11-05 specification
   - Implement required tools and resources
   - Add proper error handling and logging
   - Create comprehensive README

4. **Register in Global Config**
   - Add server to root `mcp.config` file
   - Define command, args, description, and keywords
   - Test integration with main system

### Server Independence Rules

- **No shared code**: Each server is completely self-contained
- **No cross-dependencies**: Servers cannot import from each other
- **Own configuration**: Each server manages its own environment and config
- **Standard interface**: All servers use MCP protocol for communication

## Integration with Main System

### Configuration Management
- **Global config**: `mcp.config` in project root defines all servers
- **Server discovery**: Agents automatically discover and load servers
- **Dynamic routing**: Requests routed to appropriate server based on keywords

### Communication Flow
```
Main System → Agent → MCP Manager → Individual MCP Server
                                      ↓
                                [Tool Execution]
                                      ↓
                              [Response via stdio]
```

## Testing MCP Servers

### Individual Server Testing
Each server can be tested independently:
```bash
cd mcp_server/server_name
python -m server_module  # Test server directly
```

### Integration Testing
Test via main system:
```bash
python tests/test_mcp_client.py
```

## Best Practices

### Server Development
- Use **function-based approach** over classes unless necessary
- Implement proper **error handling** and **logging**
- Follow **MCP protocol** specifications exactly
- Create **comprehensive documentation** for each server

### Dependencies
- Use **uv** for dependency management
- Lock dependencies with `uv.lock`
- Minimize external dependencies
- Use latest stable versions

### Security
- Never expose secrets in code
- Use environment variables for sensitive configuration
- Validate all inputs properly
- Implement proper error responses

## Monitoring and Debugging

### Logging
- Each server implements its own logging
- Logs are captured by the main system
- Use structured logging with clear prefixes

### Health Checks
- Servers should respond to basic MCP protocol queries
- Tool listing should work reliably
- Error responses should be properly formatted

## Future Expansion

### Planned Servers
- Document processing MCP server
- Data analysis MCP server
- File management MCP server
- Web scraping MCP server

### Extensibility
- Easy to add new servers without modifying existing code
- Plugin-like architecture for maximum flexibility
- Standard interfaces for common operations

## Contributing

When adding new MCP servers:
1. Follow the established structure and patterns
2. Ensure complete independence from other servers
3. Implement comprehensive testing
4. Update this README with server information
5. Add proper configuration to root `mcp.config`

---

**Note**: This directory is part of the Nablax Backend MCP-compliant architecture. Each server here is called via the centralized MCP manager in the `agents/` directory.