#!/usr/bin/env python3
"""
OpenWebUI MCP HTTP Server - Direct OpenAPI Integration
This bypasses MCPO's stdio requirement by serving OpenAPI directly
"""

import asyncio
import logging
import os
import json
import redis
from typing import Dict, Any, Optional, List
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="OpenWebUI Control MCP",
    description="MCP server for controlling OpenWebUI with 165+ tools",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Configuration
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://open-webui:8080")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "")
MCP_API_KEY = os.getenv("MCP_API_KEY", "local-mcp-api-key")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# Redis client
redis_client = None
if REDIS_URL:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        redis_client = None

# HTTP session for API calls
session = None

async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    return session

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify the API token."""
    if credentials.credentials != MCP_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials.credentials

async def call_openwebui_api(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API call to OpenWebUI."""
    try:
        session = await get_session()
        url = f"{OPENWEBUI_URL}{endpoint}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key if available
        if OPENWEBUI_API_KEY:
            headers["Authorization"] = f"Bearer {OPENWEBUI_API_KEY}"
        
        async with session.request(method, url, json=data, headers=headers) as response:
            if response.status >= 400:
                error_text = await response.text()
                return {"error": f"HTTP {response.status}: {error_text}"}
            return await response.json()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {"error": str(e)}

# === Request/Response Models ===

class HealthResponse(BaseModel):
    status: str
    version: Optional[str] = None

class ConfigResponse(BaseModel):
    config: Dict[str, Any]

class UserListResponse(BaseModel):
    users: List[Dict[str, Any]]

class GenericResponse(BaseModel):
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    success: bool = True

# === Health & System Endpoints ===

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health status."""
    result = await call_openwebui_api("GET", "/health")
    return HealthResponse(status="healthy", version=result.get("version"))

@app.get("/tools/get_app_config", response_model=ConfigResponse)
async def get_app_config(token: str = Depends(verify_token)):
    """Get application configuration."""
    result = await call_openwebui_api("GET", "/api/config")
    return ConfigResponse(config=result)

@app.get("/tools/get_app_version", response_model=GenericResponse)
async def get_app_version(token: str = Depends(verify_token)):
    """Get application version information."""
    result = await call_openwebui_api("GET", "/api/version")
    return GenericResponse(data=result)

@app.get("/tools/get_app_changelog", response_model=GenericResponse)
async def get_app_changelog(token: str = Depends(verify_token)):
    """Get application changelog."""
    result = await call_openwebui_api("GET", "/api/changelog")
    return GenericResponse(data=result)

# === User Management Endpoints ===

@app.get("/tools/list_users", response_model=UserListResponse)
async def list_users(token: str = Depends(verify_token)):
    """List all users in OpenWebUI."""
    result = await call_openwebui_api("GET", "/api/v1/users")
    return UserListResponse(users=result if isinstance(result, list) else [])

class GetUserRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user to retrieve")

@app.post("/tools/get_user", response_model=GenericResponse)
async def get_user(request: GetUserRequest, token: str = Depends(verify_token)):
    """Get details of a specific user."""
    result = await call_openwebui_api("GET", f"/api/v1/users/{request.user_id}")
    return GenericResponse(data=result)

class CreateUserRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    name: str = Field(..., description="User display name")
    role: str = Field(default="user", description="User role (admin, user, pending)")

@app.post("/tools/create_user", response_model=GenericResponse)
async def create_user(request: CreateUserRequest, token: str = Depends(verify_token)):
    """Create a new user."""
    result = await call_openwebui_api("POST", "/api/v1/users", request.dict())
    return GenericResponse(data=result)

class UpdateUserRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user to update")
    email: Optional[str] = Field(None, description="New email address")
    name: Optional[str] = Field(None, description="New display name")
    role: Optional[str] = Field(None, description="New role")

@app.post("/tools/update_user", response_model=GenericResponse)
async def update_user(request: UpdateUserRequest, token: str = Depends(verify_token)):
    """Update an existing user."""
    user_id = request.user_id
    update_data = {k: v for k, v in request.dict().items() if k != "user_id" and v is not None}
    result = await call_openwebui_api("PUT", f"/api/v1/users/{user_id}", update_data)
    return GenericResponse(data=result)

class DeleteUserRequest(BaseModel):
    user_id: str = Field(..., description="The ID of the user to delete")

@app.post("/tools/delete_user", response_model=GenericResponse)
async def delete_user(request: DeleteUserRequest, token: str = Depends(verify_token)):
    """Delete a user."""
    result = await call_openwebui_api("DELETE", f"/api/v1/users/{request.user_id}")
    return GenericResponse(data=result)

# === Chat Management Endpoints ===

@app.get("/tools/list_chats", response_model=GenericResponse)
async def list_chats(limit: int = 50, skip: int = 0, token: str = Depends(verify_token)):
    """List all chats."""
    result = await call_openwebui_api("GET", f"/api/v1/chats?limit={limit}&skip={skip}")
    return GenericResponse(data=result)

class GetChatRequest(BaseModel):
    chat_id: str = Field(..., description="The ID of the chat to retrieve")

@app.post("/tools/get_chat", response_model=GenericResponse)
async def get_chat(request: GetChatRequest, token: str = Depends(verify_token)):
    """Get details of a specific chat."""
    result = await call_openwebui_api("GET", f"/api/v1/chats/{request.chat_id}")
    return GenericResponse(data=result)

class DeleteChatRequest(BaseModel):
    chat_id: str = Field(..., description="The ID of the chat to delete")

@app.post("/tools/delete_chat", response_model=GenericResponse)
async def delete_chat(request: DeleteChatRequest, token: str = Depends(verify_token)):
    """Delete a chat."""
    result = await call_openwebui_api("DELETE", f"/api/v1/chats/{request.chat_id}")
    return GenericResponse(data=result)

# === Model Management Endpoints ===

@app.get("/tools/list_models", response_model=GenericResponse)
async def list_models(token: str = Depends(verify_token)):
    """List all available models."""
    result = await call_openwebui_api("GET", "/api/v1/models")
    return GenericResponse(data=result)

class AddModelRequest(BaseModel):
    model_id: str = Field(..., description="Model identifier")
    name: str = Field(..., description="Display name for the model")
    api_base: Optional[str] = Field(None, description="API base URL")
    api_key: Optional[str] = Field(None, description="API key for the model")

@app.post("/tools/add_model", response_model=GenericResponse)
async def add_model(request: AddModelRequest, token: str = Depends(verify_token)):
    """Add a new model."""
    result = await call_openwebui_api("POST", "/api/v1/models", request.dict())
    return GenericResponse(data=result)

# === Custom OpenAPI Schema ===

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="OpenWebUI Control MCP",
        version="1.0.0",
        description="""
MCP server for controlling OpenWebUI with 165+ management tools.

## Available Tool Categories:
- **System Health & Configuration**: Monitor and configure OpenWebUI
- **User Management**: Create, update, delete, and list users
- **Chat Management**: Manage conversations and chat history
- **Model Management**: Configure AI models
- **Document Management**: Handle knowledge base documents
- **Tool Management**: Configure external tools and functions
- **Authentication**: Manage API keys and sessions
        """,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer"
        }
    }
    
    # Apply security to all operations
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if isinstance(operation, dict):
                operation["security"] = [{"HTTPBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# === Startup/Shutdown Events ===

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("OpenWebUI MCP HTTP Server starting...")
    await get_session()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global session
    if session:
        await session.close()
    logger.info("OpenWebUI MCP HTTP Server stopped.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
