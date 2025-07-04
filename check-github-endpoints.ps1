$response = Invoke-RestMethod -Uri 'http://localhost:8102/openapi.json' -Headers @{'Authorization'='Bearer local-mcp-api-key'}
Write-Host "Available GitHub MCP endpoints:"
$response.paths.PSObject.Properties.Name | ForEach-Object { Write-Host "  $_" }
