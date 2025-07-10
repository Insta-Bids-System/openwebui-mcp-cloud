"""
GitHub Tools Pipeline for OpenWebUI
This pipeline enables GitHub MCP tools for all models
"""

from typing import List, Optional
import requests
import json

class Pipeline:
    def __init__(self):
        self.name = "GitHub Tools"
        
    async def on_startup(self):
        print("GitHub Tools Pipeline started")
        
    async def on_shutdown(self):
        print("GitHub Tools Pipeline stopped")
        
    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Optional[dict]:
        # Check if message asks for GitHub operations
        github_keywords = ["github", "repository", "repo", "issue", "pull request", "search code"]
        
        if any(keyword in user_message.lower() for keyword in github_keywords):
            # Add tool information to the prompt
            enhanced_message = f"""
You have access to GitHub tools at http://localhost:8102. Available endpoints:
- /search_repositories - Search for repositories
- /create_repository - Create new repository  
- /get_file_contents - Read files from repos
- /create_issue - Create issues
- /list_issues - List issues

User request: {user_message}

Please use the appropriate tool to fulfill this request.
"""
            
            # Update the message
            if messages and messages[-1]["role"] == "user":
                messages[-1]["content"] = enhanced_message
                
        return body
