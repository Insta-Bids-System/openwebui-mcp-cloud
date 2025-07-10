#!/usr/bin/env python3
"""
Simple GitHub MCP Proxy with Owner Injection
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
DEFAULT_GITHUB_OWNER = "Insta-Bids-System"
GITHUB_MCP_BASE_URL = "http://local-mcpo-github-internal:8000"
MCP_API_KEY = os.getenv("MCP_API_KEY", "local-mcp-key-for-testing")

def inject_owner(data):
    """Inject default owner into query string if missing or invalid"""
    if isinstance(data, dict) and "query" in data:
        query = data["query"]
        
        # Check if query already has user: or org: prefix
        if not ("user:" in query or "org:" in query):
            # Add user prefix for the default owner
            data["query"] = f"user:{DEFAULT_GITHUB_OWNER} {query}".strip()
            logger.info(f"🔧 Injected user:{DEFAULT_GITHUB_OWNER} into query: {data['query']}")
        else:
            # Replace "your_username" with actual owner
            if "user:your_username" in query:
                data["query"] = query.replace("user:your_username", f"user:{DEFAULT_GITHUB_OWNER}")
                logger.info(f"🔧 Replaced your_username with {DEFAULT_GITHUB_OWNER}: {data['query']}")
            elif "user:your_github_username" in query:
                data["query"] = query.replace("user:your_github_username", f"user:{DEFAULT_GITHUB_OWNER}")
                logger.info(f"🔧 Replaced your_github_username with {DEFAULT_GITHUB_OWNER}: {data['query']}")
    
    # Handle other operations that need owner parameter
    owner_operations = ["create_repository", "update_repository", "delete_repository", 
                       "create_or_update_file", "delete_file", "get_file_contents",
                       "list_files", "push_files"]
    
    # Check if this looks like one of the operations that needs owner parameter
    if isinstance(data, dict):
        # If owner is missing or invalid, add it
        if "owner" in data and data["owner"] in ["your_username", "your_github_username", "", None]:
            data["owner"] = DEFAULT_GITHUB_OWNER
            logger.info(f"🔧 Fixed owner parameter: {DEFAULT_GITHUB_OWNER}")
        elif "owner" not in data and any(op in str(data).lower() for op in owner_operations):
            data["owner"] = DEFAULT_GITHUB_OWNER
            logger.info(f"🔧 Added missing owner parameter: {DEFAULT_GITHUB_OWNER}")
    
    return data

async def proxy_all(request):
    """Proxy all requests to GitHub MCP"""
    method = request.method
    path = request.url.path
    query = str(request.url.query) if request.url.query else ""
    full_path = f"{path}?{query}" if query else path
    
    logger.info(f"📡 {method} {full_path}")
    
    try:
        # Handle request body
        json_payload = None
        if method in ['POST', 'PUT', 'PATCH']:
            body = await request.body()
            logger.info(f"🔍 Original body size: {len(body)} bytes")
            logger.info(f"🔍 Original body: {body}")
            
            if body:
                try:
                    original_data = json.loads(body)
                    logger.info(f"🔍 Original JSON: {original_data}")
                    
                    json_payload = inject_owner(original_data.copy())
                    logger.info(f"🔍 Modified JSON: {json_payload}")
                    
                    # Calculate new size
                    new_body = json.dumps(json_payload)
                    logger.info(f"🔍 New body size: {len(new_body)} bytes")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"🔍 JSON decode error: {e}")
                    json_payload = None
        
        # Make request to GitHub MCP
        async with httpx.AsyncClient() as client:
            logger.info(f"🔍 Sending to: {GITHUB_MCP_BASE_URL}{full_path}")
            logger.info(f"🔍 JSON payload: {json_payload}")
            
            response = await client.request(
                method=method,
                url=f"{GITHUB_MCP_BASE_URL}{full_path}",
                json=json_payload,
                headers={"Authorization": f"Bearer {MCP_API_KEY}"},
                timeout=30.0
            )
            
            logger.info(f"✅ {method} {full_path} -> {response.status_code}")
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except Exception as e:
        logger.error(f"❌ Error details: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return Response(
            content=json.dumps({"error": str(e)}),
            status_code=500,
            media_type="application/json"
        )

# Routes
routes = [
    Route("/{path:path}", proxy_all, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
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