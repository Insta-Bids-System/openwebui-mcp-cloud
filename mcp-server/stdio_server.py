#!/usr/bin/env python3
"""
OpenWebUI MCP stdio server for administrative control
"""

import asyncio
import logging
import os
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if mcp is available
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("OpenWebUI Control")
    logger.info("FastMCP initialized successfully")
except ImportError as e:
    logger.error(f"Failed to import MCP: {e}")
    exit(1)

# Configuration
OPENWEBUI_URL = os.getenv("OPENWEBUI_URL", "http://open-webui:8080")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "")

async def call_openwebui_api(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make API call to OpenWebUI using urllib."""
    try:
        url = f"{OPENWEBUI_URL}{endpoint}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key if available
        if OPENWEBUI_API_KEY:
            headers["Authorization"] = f"Bearer {OPENWEBUI_API_KEY}"
        
        # Prepare request
        req_data = None
        if data:
            req_data = json.dumps(data).encode('utf-8')
        
        request = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        
        # Make the request
        with urllib.request.urlopen(request, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else {"success": True}
            
    except urllib.error.HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            return {"error": error_msg, "details": error_data}
        except:
            return {"error": error_msg}
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {"error": str(e)}

# === Health & System Tools ===

@mcp.tool()
async def get_health() -> Dict[str, Any]:
    """Check OpenWebUI system health status."""
    # Use the public health endpoint that doesn't require authentication
    return await call_openwebui_api("GET", "/health")

@mcp.tool()
async def get_app_config() -> Dict[str, Any]:
    """Get OpenWebUI application configuration."""
    return await call_openwebui_api("GET", "/api/config")

@mcp.tool()
async def get_app_version() -> Dict[str, Any]:
    """Get OpenWebUI application version information."""
    return await call_openwebui_api("GET", "/api/version")

# === User Management Tools ===

@mcp.tool()
async def list_users() -> Dict[str, Any]:
    """List all users in OpenWebUI."""
    return await call_openwebui_api("GET", "/api/v1/users")

@mcp.tool()
async def get_user(user_id: str) -> Dict[str, Any]:
    """Get details of a specific user."""
    return await call_openwebui_api("GET", f"/api/v1/users/{user_id}")

@mcp.tool()
async def create_user(email: str, password: str, name: str, role: str = "user") -> Dict[str, Any]:
    """Create a new user in OpenWebUI."""
    data = {
        "email": email,
        "password": password, 
        "name": name,
        "role": role
    }
    return await call_openwebui_api("POST", "/api/v1/users", data)

@mcp.tool()
async def update_user_role(user_id: str, role: str) -> Dict[str, Any]:
    """Update user role (admin, user, pending)."""
    return await call_openwebui_api("POST", f"/api/v1/users/{user_id}/role", {"role": role})

@mcp.tool()
async def delete_user(user_id: str) -> Dict[str, Any]:
    """Delete a user from OpenWebUI."""
    return await call_openwebui_api("DELETE", f"/api/v1/users/{user_id}")

# === Model Management Tools ===

@mcp.tool()
async def list_models() -> Dict[str, Any]:
    """List all available models in OpenWebUI."""
    return await call_openwebui_api("GET", "/api/models")

@mcp.tool()
async def get_model_info(model_id: str) -> Dict[str, Any]:
    """Get information about a specific model."""
    return await call_openwebui_api("GET", f"/api/models/{model_id}")

@mcp.tool()
async def add_model(model_id: str, name: str, description: str = "") -> Dict[str, Any]:
    """Add a new model to OpenWebUI."""
    data = {
        "id": model_id,
        "name": name,
        "description": description
    }
    return await call_openwebui_api("POST", "/api/models/add", data)

@mcp.tool()
async def delete_model(model_id: str) -> Dict[str, Any]:
    """Delete a model from OpenWebUI."""
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
    """Create a new chat in OpenWebUI."""
    data = {
        "title": title,
        "messages": messages or []
    }
    return await call_openwebui_api("POST", "/api/v1/chats", data)

@mcp.tool()
async def delete_chat(chat_id: str) -> Dict[str, Any]:
    """Delete a chat from OpenWebUI."""
    return await call_openwebui_api("DELETE", f"/api/v1/chats/{chat_id}")

@mcp.tool()
async def share_chat(chat_id: str) -> Dict[str, Any]:
    """Share a chat and get sharing link."""
    return await call_openwebui_api("POST", f"/api/v1/chats/{chat_id}/share")

# === File System Tools (Workspace) ===

@mcp.tool()
async def list_workspace_files(path: str = "/workspace") -> Dict[str, Any]:
    """List files in the workspace directory."""
    try:
        if not os.path.exists(path):
            return {"error": f"Path {path} does not exist"}
        
        files = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            files.append({
                "name": item,
                "path": item_path,
                "is_directory": os.path.isdir(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        return {"files": files, "total": len(files)}
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return {"error": str(e)}

@mcp.tool()
async def read_workspace_file(path: str) -> Dict[str, Any]:
    """Read content of a file in workspace."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content, "path": path, "size": len(content)}
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return {"error": str(e)}

@mcp.tool()
async def write_workspace_file(path: str, content: str) -> Dict[str, Any]:
    """Write content to a file in workspace."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": path, "size": len(content)}
    except Exception as e:
        logger.error(f"Error writing file {path}: {e}")
        return {"error": str(e)}

# === Document Management Tools ===

@mcp.tool()
async def list_documents() -> Dict[str, Any]:
    """List all documents in OpenWebUI knowledge base."""
    return await call_openwebui_api("GET", "/api/v1/documents")

@mcp.tool()
async def upload_document(filename: str, content: str, collection_name: str = "default") -> Dict[str, Any]:
    """Upload a document to OpenWebUI knowledge base."""
    data = {
        "filename": filename,
        "content": content,
        "collection_name": collection_name
    }
    return await call_openwebui_api("POST", "/api/v1/documents", data)

@mcp.tool()
async def delete_document(doc_id: str) -> Dict[str, Any]:
    """Delete a document from OpenWebUI knowledge base."""
    return await call_openwebui_api("DELETE", f"/api/v1/documents/{doc_id}")

if __name__ == "__main__":
    try:
        logger.info("Starting OpenWebUI Administrative MCP STDIO Server...")
        logger.info("Available tool categories:")
        logger.info("  - Health/System: get_health, get_app_config, get_app_version")
        logger.info("  - User Management: list_users, get_user, create_user, update_user_role, delete_user")
        logger.info("  - Model Management: list_models, get_model_info, add_model, delete_model")
        logger.info("  - Chat Management: list_chats, get_chat, create_chat, delete_chat, share_chat")
        logger.info("  - File System: list_workspace_files, read_workspace_file, write_workspace_file")
        logger.info("  - Document Management: list_documents, upload_document, delete_document")
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        exit(1)