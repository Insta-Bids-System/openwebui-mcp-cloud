# test-mcp-endpoints.ps1 - Test all MCP endpoints

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Testing MCP Endpoints" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Function to test endpoint
function Test-MCPEndpoint {
    param(
        [string]$Name,
        [string]$Port,
        [string]$TestPath = "/openapi.json"
    )
    
    Write-Host "`nTesting $Name (Port $Port)..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$Port$TestPath" -Method Get -ErrorAction Stop
        $toolCount = ($response.paths.PSObject.Properties | Measure-Object).Count
        Write-Host "✅ SUCCESS: $toolCount tools available" -ForegroundColor Green
        
        # Show first 5 tools
        if ($toolCount -gt 0) {
            Write-Host "   Sample tools:" -ForegroundColor Gray
            $response.paths.PSObject.Properties.Name | Select-Object -First 5 | ForEach-Object {
                Write-Host "   - $_" -ForegroundColor Gray
            }
        }
    }
    catch {
        Write-Host "❌ FAILED: $_" -ForegroundColor Red
        Write-Host "   Check logs: docker logs local-mcpo-$($Name.ToLower())" -ForegroundColor Yellow
    }
}

# Test each service
Test-MCPEndpoint -Name "OpenWebUI" -Port "8101"
Test-MCPEndpoint -Name "GitHub" -Port "8102"
Test-MCPEndpoint -Name "Filesystem" -Port "8103"
Test-MCPEndpoint -Name "Brave-Search" -Port "8104"
Test-MCPEndpoint -Name "Memory" -Port "8105"

Write-Host "`n====================================" -ForegroundColor Cyan
Write-Host "Test Complete" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Test specific tool execution
Write-Host "`nTesting tool execution (OpenWebUI health check)..." -ForegroundColor Yellow

$headers = @{
    "Authorization" = "Bearer local-mcp-api-key"
    "Content-Type" = "application/json"
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8101/get_health" `
        -Method Post `
        -Headers $headers `
        -Body '{}' `
        -ErrorAction Stop
    
    Write-Host "✅ Tool execution successful!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
}
catch {
    Write-Host "❌ Tool execution failed: $_" -ForegroundColor Red
}

Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
