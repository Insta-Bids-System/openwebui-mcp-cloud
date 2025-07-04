import requests

async def github_search(query: str) -> str:
    """
    Search GitHub repositories
    Example: github_search("language:python stars:>100")
    """
    url = "http://localhost:8102/search_repositories"
    headers = {
        "Authorization": "Bearer local-mcp-key-for-testing",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json={"query": query})
    data = response.json()
    
    if "error" in data:
        return f"Error: {data['error']}"
    
    total = data.get('total_count', 0)
    items = data.get('items', [])[:5]
    
    result = f"Found {total} repositories\n\n"
    for repo in items:
        result += f"- {repo['full_name']} ({repo['stargazers_count']} stars)\n"
    
    return result
