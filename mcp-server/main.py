from mcp.server.fastmcp import FastMCP
import aiohttp
import asyncio
import os
import redis
import json
import urllib.parse
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP("OpenWebUI Control")

# Configuration
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://open-webui:8080")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "")

# Redis client with Valkey fix
redis_client = None
if REDIS_URL:
    redis_url_fixed = f"{REDIS_URL}?ssl_cert_reqs=none&decode_responses=true"
    try:
        redis_client = redis.from_url(redis_url_fixed)
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
async def parse_request_data(request_data: Any) -> Dict[str, Any]:
    """Parse request data handling multiple content types."""
    if isinstance(request_data, dict):
        return request_data
    
    if isinstance(request_data, str):
        try:
            return json.loads(request_data)
        except:
            # Try parsing as form data
            parsed = urllib.parse.parse_qs(request_data)
            if 'data' in parsed:
                return json.loads(parsed['data'][0])
    return {}

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
            return await response.json()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {"error": str(e)}

# === Health & System Tools ===

@mcp.tool()
async def get_health() -> Dict[str, Any]:
    """Check system health status."""
    return await call_openwebui_api("GET", "/health")
@mcp.tool()
async def get_app_config() -> Dict[str, Any]:
    """Get application configuration."""
    return await call_openwebui_api("GET", "/api/config")

@mcp.tool()
async def get_app_changelog() -> Dict[str, Any]:
    """Get application changelog."""
    return await call_openwebui_api("GET", "/api/changelog")

@mcp.tool()
async def get_app_version() -> Dict[str, Any]:
    """Get application version information."""
    return await call_openwebui_api("GET", "/api/version")

# === User Management Tools ===

@mcp.tool()
async def list_users() -> Dict[str, Any]:
    """List all users in the system."""
    return await call_openwebui_api("GET", "/api/v1/users")

@mcp.tool()
async def get_user(user_id: str) -> Dict[str, Any]:
    """Get details of a specific user."""
    return await call_openwebui_api("GET", f"/api/v1/users/{user_id}")

@mcp.tool()
async def create_user(email: str, password: str, name: str, role: str = "user") -> Dict[str, Any]:
    """Create a new user."""
    data = {
        "email": email,
        "password": password, 
        "name": name,
        "role": role
    }
    return await call_openwebui_api("POST", "/api/v1/users", data)
@mcp.tool()
async def update_user(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update user information."""
    return await call_openwebui_api("PUT", f"/api/v1/users/{user_id}", updates)

@mcp.tool()
async def delete_user(user_id: str) -> Dict[str, Any]:
    """Delete a user."""
    return await call_openwebui_api("DELETE", f"/api/v1/users/{user_id}")

@mcp.tool()
async def update_user_role(user_id: str, role: str) -> Dict[str, Any]:
    """Update user role (admin, user, pending)."""
    return await call_openwebui_api("POST", f"/api/v1/users/{user_id}/role", {"role": role})

# === Model Management Tools ===

@mcp.tool()
async def list_models() -> Dict[str, Any]:
    """List all available models."""
    return await call_openwebui_api("GET", "/api/models")

@mcp.tool()
async def get_model_info(model_id: str) -> Dict[str, Any]:
    """Get information about a specific model."""
    return await call_openwebui_api("GET", f"/api/models/{model_id}")

@mcp.tool()
async def add_model(model_id: str, name: str, description: str = "") -> Dict[str, Any]:
    """Add a new model to the system."""
    data = {
        "id": model_id,
        "name": name,
        "description": description
    }
    return await call_openwebui_api("POST", "/api/models/add", data)
@mcp.tool()
async def delete_model(model_id: str) -> Dict[str, Any]:
    """Delete a model from the system."""
    return await call_openwebui_api("DELETE", f"/api/models/{model_id}")

# === Chat Management Tools ===

@mcp.tool()
async def list_chats(user_id: Optional[str] = None) -> Dict[str, Any]:
    """List all chats, optionally filtered by user."""
    endpoint = "/api/v1/chats"
    if user_id:
        endpoint = f"/api/v1/chats/user/{user_id}"
    return await call_openwebui_api("GET", endpoint)

@mcp.tool()
async def get_chat(chat_id: str) -> Dict[str, Any]:
    """Get details of a specific chat."""
    return await call_openwebui_api("GET", f"/api/v1/chats/{chat_id}")

@mcp.tool()
async def create_chat(title: str, messages: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new chat."""
    data = {
        "title": title,
        "messages": messages or []
    }
    return await call_openwebui_api("POST", "/api/v1/chats", data)

@mcp.tool()
async def update_chat(chat_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update chat information."""
    return await call_openwebui_api("PUT", f"/api/v1/chats/{chat_id}", updates)
@mcp.tool()
async def delete_chat(chat_id: str) -> Dict[str, Any]:
    """Delete a chat."""
    return await call_openwebui_api("DELETE", f"/api/v1/chats/{chat_id}")

@mcp.tool()
async def share_chat(chat_id: str) -> Dict[str, Any]:
    """Share a chat and get sharing link."""
    return await call_openwebui_api("POST", f"/api/v1/chats/{chat_id}/share")

@mcp.tool()
async def archive_chat(chat_id: str) -> Dict[str, Any]:
    """Archive a chat."""
    return await call_openwebui_api("POST", f"/api/v1/chats/{chat_id}/archive")

# === File System Tools ===

@mcp.tool()
async def list_files(path: str = "/workspace") -> Dict[str, Any]:
    """List files in a directory."""
    try:
        files = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            files.append({
                "name": item,
                "path": item_path,
                "is_directory": os.path.isdir(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}
@mcp.tool()
async def read_file(path: str) -> Dict[str, Any]:
    """Read content of a file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content, "path": path}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def write_file(path: str, content: str) -> Dict[str, Any]:
    """Write content to a file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": path}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def delete_file(path: str) -> Dict[str, Any]:
    """Delete a file or directory."""
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        return {"success": True, "path": path}
    except Exception as e:
        return {"error": str(e)}
@mcp.tool()
async def create_directory(path: str) -> Dict[str, Any]:
    """Create a new directory."""
    try:
        os.makedirs(path, exist_ok=True)
        return {"success": True, "path": path}
    except Exception as e:
        return {"error": str(e)}

# === Document & Knowledge Base Tools ===

@mcp.tool()
async def list_documents() -> Dict[str, Any]:
    """List all documents in the knowledge base."""
    return await call_openwebui_api("GET", "/api/v1/documents")

@mcp.tool()
async def upload_document(filename: str, content: str, collection_name: str = "default") -> Dict[str, Any]:
    """Upload a document to the knowledge base."""
    data = {
        "filename": filename,
        "content": content,
        "collection_name": collection_name
    }
    return await call_openwebui_api("POST", "/api/v1/documents", data)

@mcp.tool()
async def delete_document(doc_id: str) -> Dict[str, Any]:
    """Delete a document from the knowledge base."""
    return await call_openwebui_api("DELETE", f"/api/v1/documents/{doc_id}")

# === Main Server Loop ===

if __name__ == "__main__":
    logger.info("Starting MCP Server...")
    logger.info(f"OpenWebUI URL: {OPENWEBUI_URL}")
    logger.info(f"Redis connected: {redis_client is not None}")
    
    # Run the MCP server
    mcp.run()