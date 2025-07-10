import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI(title="MCP Path Fixer Proxy")

# Backend MCP services
SERVICES = {
    "filesystem": "http://local-mcpo-filesystem:8000",
    "github": "http://local-mcpo-github-internal:8000",
    "memory": "http://local-mcpo-memory:8000"
}

class ToolRequest(BaseModel):
    tool: str
    parameters: dict

def fix_file_path(path: str) -> str:
    """Fix common path issues"""
    # Remove /app/ prefix
    if path.startswith("/app/"):
        path = path[5:]
    
    # Remove C:\ or other Windows paths
    if re.match(r'^[A-Za-z]:\\', path):
        path = os.path.basename(path)
    
    # Remove leading slashes for relative paths
    if path.startswith("/") and not path.startswith("/workspace"):
        path = path[1:]
    
    return path

@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """Execute tool with path fixing"""
    tool_name = request.tool
    params = request.parameters
    
    # Fix paths for filesystem operations
    if tool_name in ["write_file", "read_file", "create_directory"]:
        if "path" in params:
            original_path = params["path"]
            fixed_path = fix_file_path(original_path)
            params["path"] = fixed_path
            print(f"Fixed path: {original_path} -> {fixed_path}")
    
    # Forward to appropriate service
    service_url = SERVICES.get("filesystem")  # Default to filesystem
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{service_url}/{tool_name}",
            json=params
        )
        
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    
    return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)