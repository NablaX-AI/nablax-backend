"""
Nablax Backend - Main FastAPI Application Entry Point
MCP-compliant three-tier email reply service with function-based architecture.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.email_router import router as email_router
from agents.mcp_manager import load_mcp_config, get_mcp_servers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Nablax Backend API",
        description="MCP-compliant three-tier email reply service with function-based architecture",
        version="2.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(email_router)
    
    return app

# Create application instance
app = create_app()

# Setup routes
from routes import setup_main_routes, setup_agent_routes, setup_system_routes

setup_main_routes(app)
setup_agent_routes(app)
setup_system_routes(app)

# Initialize MCP configuration
load_mcp_config()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)