# Fix the MCP decorators by replacing @mcp.tool with @mcp.tool()
$content = Get-Content "mcp-server\main.py" -Raw
$fixed = $content -replace '@mcp\.tool\r?\n', "@mcp.tool()`r`n"
Set-Content "mcp-server\main.py" $fixed -NoNewline
Write-Host "Fixed MCP decorators in main.py"