# Local Git MCP Server
# This works with LOCAL repositories on your server, like Claude Desktop

import os
import json
import subprocess
from pathlib import Path
from mcp.server import Server
from mcp.types import TextContent, Tool, ToolResponse

# Initialize MCP server
mcp = Server("local-git")

# Configure workspace directory
WORKSPACE_DIR = os.getenv("WORKSPACE_DIR", "/workspace")
REPOS_DIR = os.getenv("REPOS_DIR", "/repos")

@mcp.tool()
async def list_local_repositories():
    """List all git repositories in the workspace"""
    repos = []
    
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        if '.git' in dirs:
            repo_path = Path(root)
            repo_name = repo_path.name
            
            # Get git status
            try:
                status = subprocess.check_output(
                    ['git', 'status', '--porcelain'], 
                    cwd=root, 
                    text=True
                )
                has_changes = bool(status.strip())
                
                # Get current branch
                branch = subprocess.check_output(
                    ['git', 'branch', '--show-current'], 
                    cwd=root, 
                    text=True
                ).strip()
                
                repos.append({
                    "name": repo_name,
                    "path": str(repo_path),
                    "branch": branch,
                    "has_changes": has_changes,
                    "status": "modified" if has_changes else "clean"
                })
            except:
                pass
