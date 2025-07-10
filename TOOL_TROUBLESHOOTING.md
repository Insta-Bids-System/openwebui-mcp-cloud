# OpenWebUI Tool Registration Helper

## Quick Fix for GitHub Tools Not Working

### Option 1: Direct API Test (Verify Tools Work)
Run this in PowerShell to test the GitHub tools directly:

```powershell
# Test search
$headers = @{
    "Authorization" = "Bearer local-mcp-key-for-testing"
    "Content-Type" = "application/json"
}

$body = @{
    query = "language:python stars:>100"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "http://localhost:8102/search_repositories" -Method POST -Headers $headers -Body $body
Write-Host "Found $($result.total_count) repositories"
```

### Option 2: Force Tool Usage in Chat

Use these exact prompts:

1. **Search**: 
   ```
   Execute POST request to http://localhost:8102/search_repositories with body {"query": "language:python stars:>100"}
   ```

2. **Create Repo**:
   ```
   Execute POST request to http://localhost:8102/create_repository with body {"name": "test-repo", "description": "Test", "private": true}
   ```

### Option 3: Install Function Calling Model

Some models don't support function calling well. Consider:

1. **Install Ollama**: https://ollama.ai
2. **Pull a function-calling model**:
   ```
   ollama pull mistral
   ollama pull llama2
   ```
3. **Configure in OpenWebUI**: Settings → Models → Add Ollama URL

### Option 4: Check Tool Format

The tool might need to be in OpenWebUI's function format. Try adding a "Function" instead:

1. Go to Settings → Functions
2. Create New Function
3. Add this code:

```python
import requests

def search_github_repos(query):
    """Search GitHub repositories"""
    headers = {
        "Authorization": "Bearer local-mcp-key-for-testing",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "http://localhost:8102/search_repositories",
        json={"query": query},
        headers=headers
    )
    
    return response.json()
```

### Option 5: Enable Debug Mode

1. Check OpenWebUI logs:
   ```
   docker logs local-open-webui --tail 50
   ```

2. Check if tools are being loaded:
   ```
   docker exec local-open-webui cat /app/backend/data/config.json | grep -i tool
   ```
