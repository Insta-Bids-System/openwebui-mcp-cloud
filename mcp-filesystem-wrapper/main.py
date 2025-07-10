#!/usr/bin/env python3
"""
Filesystem MCP Wrapper with Auto-Path Normalization
Automatically converts relative paths to /workspace absolute paths
"""

import json
import logging
import httpx
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
WORKSPACE_BASE = "/workspace"
FILESYSTEM_MCP_BASE_URL = "http://local-mcpo-filesystem:8000"
MCP_API_KEY = os.getenv("MCP_API_KEY", "local-mcp-key-for-testing")

def normalize_path(path):
    """Convert relative paths to /workspace absolute paths"""
    if not path:
        return WORKSPACE_BASE
    
    # Already absolute and starts with /workspace
    if path.startswith("/workspace"):
        return path
    
    # Current directory references
    if path in [".", "./"]:
        return WORKSPACE_BASE
    
    # Relative paths - prepend /workspace
    if not path.startswith("/"):
        return f"{WORKSPACE_BASE}/{path}"
    
    # Other absolute paths - might be intentional
    return path

def redirect_tool_calls(data, path):
    """Redirect OpenWebUI tool calls to filesystem MCP equivalents"""
    
    # Tool redirection mapping
    tool_redirects = {
        "/list_workspace_files": "/list_directory",
        "/read_workspace_file": "/read_file", 
        "/write_workspace_file": "/write_file"
    }
    
    # Check if this is a redirected tool call
    for old_path, new_path in tool_redirects.items():
        if path == old_path:
            logger.info(f"🔄 Redirecting {old_path} → {new_path}")
            return new_path, data
    
    return path, data

def enhance_filesystem_request(data, path):
    """Enhance filesystem requests with path normalization"""
    if not isinstance(data, dict):
        return data
    
    # Normalize path parameter
    if "path" in data:
        original_path = data["path"]
        normalized_path = normalize_path(original_path)
        
        if original_path != normalized_path:
            data["path"] = normalized_path
            logger.info(f"🔧 Path normalized: '{original_path}' → '{normalized_path}'")
    
    # Handle list_workspace_files default path
    if path == "/list_directory" and "path" not in data:
        data["path"] = WORKSPACE_BASE
        logger.info(f"🔧 Added default workspace path: {WORKSPACE_BASE}")
    
    return data

async def proxy_filesystem(request):
    """Proxy filesystem requests with enhancements"""
    method = request.method
    path = request.url.path
    query = str(request.url.query) if request.url.query else ""
    full_path = f"{path}?{query}" if query else path
    
    logger.info(f"📁 {method} {full_path}")
    
    try:
        # Handle request body
        json_payload = None
        if method in ['POST', 'PUT', 'PATCH']:
            body = await request.body()
            if body:
                try:
                    json_payload = json.loads(body)
                    logger.info(f"🔍 Original request: {json_payload}")
                    
                    # Apply tool redirection
                    redirected_path, json_payload = redirect_tool_calls(json_payload, path)
                    if redirected_path != path:
                        path = redirected_path
                        full_path = f"{path}?{query}" if query else path
                    
                    # Apply filesystem enhancements
                    json_payload = enhance_filesystem_request(json_payload, path)
                    logger.info(f"🔧 Enhanced request: {json_payload}")
                    
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON payload")
        
        # Forward to filesystem MCP
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{FILESYSTEM_MCP_BASE_URL}{full_path}",
                json=json_payload if json_payload else None,
                headers={"Authorization": f"Bearer {MCP_API_KEY}"},
                timeout=30.0
            )
            
            logger.info(f"✅ {method} {full_path} → {response.status_code}")
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )

async def openapi_proxy(request):
    """Forward OpenAPI schema from filesystem MCP"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{FILESYSTEM_MCP_BASE_URL}/openapi.json",
                headers={"Authorization": f"Bearer {MCP_API_KEY}"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                schema = response.json()
                # Optionally modify schema to reflect wrapper enhancements
                schema["info"]["title"] = "Enhanced Filesystem MCP"
                schema["info"]["description"] = "Filesystem MCP with auto-path normalization"
                return Response(
                    content=json.dumps(schema),
                    status_code=200,
                    media_type="application/json"
                )
            else:
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
    except Exception as e:
        logger.error(f"❌ OpenAPI error: {e}")
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )

# Routes
routes = [
    Route("/openapi.json", openapi_proxy, methods=["GET"]),
    Route("/{path:path}", proxy_filesystem, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
]

# Create app
app = Starlette(routes=routes)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 