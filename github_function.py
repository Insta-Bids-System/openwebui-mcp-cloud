"""
GitHub Tools Function for OpenWebUI
This function provides GitHub operations through MCP tools
"""

import json
import requests
from typing import Dict, Any, List, Optional

class GitHubTools:
    def __init__(self):
        self.base_url = "http://localhost:8102"
        self.headers = {
            "Authorization": "Bearer local-mcp-key-for-testing",
            "Content-Type": "application/json"
        }
    
    def search_repositories(self, query: str) -> Dict[str, Any]:
        """Search GitHub repositories"""
        response = requests.post(
            f"{self.base_url}/search_repositories",
            headers=self.headers,
            json={"query": query}
        )
        return response.json()
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict[str, Any]:
        """Create a new GitHub repository"""
        response = requests.post(
            f"{self.base_url}/create_repository",
            headers=self.headers,
            json={
                "name": name,
                "description": description,
                "private": private
            }
        )
        return response.json()
    
    def get_file_contents(self, owner: str, repo: str, path: str) -> Dict[str, Any]:
        """Get file contents from a repository"""
        response = requests.post(
            f"{self.base_url}/get_file_contents",
            headers=self.headers,
            json={
                "owner": owner,
                "repo": repo,
                "path": path
            }
        )
        return response.json()
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> Dict[str, Any]:
        """Create an issue in a repository"""
        response = requests.post(
            f"{self.base_url}/create_issue",
            headers=self.headers,
            json={
                "owner": owner,
                "repo": repo,
                "title": title,
                "body": body
            }
        )
        return response.json()

# Main function that OpenWebUI will call
async def main(query: str):
    """
    Main function for GitHub operations
    Examples:
    - "search python repos with 100+ stars"
    - "create repo named test-repo"
    - "read README.md from microsoft/vscode"
    """
    
    github = GitHubTools()
    
    # Parse the query to determine action
    query_lower = query.lower()
    
    if "search" in query_lower:
        # Extract search parameters
        if "python" in query_lower:
            search_query = "language:python"
            if "stars" in query_lower or "100" in query_lower:
                search_query += " stars:>100"
        else:
            search_query = query.replace("search", "").strip()
        
        result = github.search_repositories(search_query)
        return f"Found {result.get('total_count', 0)} repositories. Top results: " + \
               ", ".join([f"{r['full_name']} ({r['stargazers_count']} stars)" 
                         for r in result.get('items', [])[:5]])
    
    elif "create repo" in query_lower or "create repository" in query_lower:
        # Extract repo name
        import re
        match = re.search(r'named?\s+([^\s]+)', query)
        if match:
            repo_name = match.group(1).strip('"\'')
            result = github.create_repository(repo_name, "Created via OpenWebUI", True)
            return f"Repository '{repo_name}' created successfully!"
        else:
            return "Please specify a repository name"
    
    elif "read" in query_lower or "get" in query_lower:
        # Extract file path and repo
        parts = query.split("from")
        if len(parts) == 2:
            file_path = parts[0].replace("read", "").replace("get", "").strip()
            repo_parts = parts[1].strip().split("/")
            if len(repo_parts) == 2:
                result = github.get_file_contents(repo_parts[0], repo_parts[1], file_path)
                return f"File '{file_path}' from {parts[1].strip()} - Size: {result.get('size', 0)} bytes"
        return "Please specify file and repository (e.g., 'read README.md from owner/repo')"
    
    else:
        return """Available GitHub operations:
        - Search: 'search python repos with 100+ stars'
        - Create repo: 'create repo named my-test-repo'
        - Read file: 'read README.md from microsoft/vscode'
        - Create issue: 'create issue in owner/repo'
        """
