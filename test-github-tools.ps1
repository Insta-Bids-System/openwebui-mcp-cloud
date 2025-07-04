# Test GitHub MCP Tools
Write-Host "Testing GitHub MCP Tools Setup..." -ForegroundColor Cyan

# Test 1: Check if MCPO is running
Write-Host "`n1. Checking MCPO GitHub Server..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8102/openapi.json" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✓ MCPO server is running" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ MCPO server is not accessible" -ForegroundColor Red
}

# Test 2: List available tools
Write-Host "`n2. Available GitHub Tools:" -ForegroundColor Yellow
try {
    $openapi = Invoke-RestMethod -Uri "http://localhost:8102/openapi.json"
    $tools = $openapi.paths.PSObject.Properties.Name
    foreach ($tool in $tools | Select-Object -First 10) {
        Write-Host "   - $tool" -ForegroundColor Green
    }
    Write-Host "   ... and $($tools.Count - 10) more tools" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Could not retrieve tool list" -ForegroundColor Red
}

# Test 3: Test authentication
Write-Host "`n3. Testing Authentication..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer local-mcp-key-for-testing"
    "Content-Type" = "application/json"
}

try {
    # Test list_repositories endpoint
    $body = @{} | ConvertTo-Json
    $result = Invoke-RestMethod -Uri "http://localhost:8102/list_repositories" -Method POST -Headers $headers -Body $body
    Write-Host "   ✓ Authentication successful" -ForegroundColor Green
    Write-Host "   ✓ Found $($result.repositories.Count) repositories" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Authentication failed: $_" -ForegroundColor Red
}

Write-Host "`n4. Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open http://localhost:8080" -ForegroundColor White
Write-Host "   2. Go to Settings -> Tools" -ForegroundColor White
Write-Host "   3. Add new tool with:" -ForegroundColor White
Write-Host "      - API Base URL: http://localhost:8102" -ForegroundColor Yellow
Write-Host "      - Bearer Token: local-mcp-key-for-testing" -ForegroundColor Yellow
