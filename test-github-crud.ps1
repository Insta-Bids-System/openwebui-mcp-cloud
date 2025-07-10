# GitHub MCP CRUD Test Script
$headers = @{
    "Authorization" = "Bearer local-mcp-key-for-testing"
    "Content-Type" = "application/json"
}

Write-Host "GitHub MCP CRUD Operations Test" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Test 1: Search Repositories
Write-Host "`n1. Testing Repository Search..." -ForegroundColor Yellow
try {
    $searchBody = @{
        query = "language:javascript stars:>1000"
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8102/search_repositories" -Method POST -Headers $headers -Body $searchBody
    Write-Host "   ✓ Found $($result.total_count) repositories" -ForegroundColor Green
    Write-Host "   ✓ Top result: $($result.items[0].full_name) with $($result.items[0].stargazers_count) stars" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Search failed: $_" -ForegroundColor Red
}

# Test 2: Get File Contents
Write-Host "`n2. Testing File Read..." -ForegroundColor Yellow
try {
    $fileBody = @{
        owner = "microsoft"
        repo = "vscode"
        path = "README.md"
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8102/get_file_contents" -Method POST -Headers $headers -Body $fileBody
    Write-Host "   ✓ Successfully read file: $($result.name)" -ForegroundColor Green
    Write-Host "   ✓ File size: $($result.size) bytes" -ForegroundColor Green
} catch {
    Write-Host "   ✗ File read failed: $_" -ForegroundColor Red
}

# Test 3: List Issues
Write-Host "`n3. Testing Issue Listing..." -ForegroundColor Yellow
try {
    $issueBody = @{
        owner = "facebook"
        repo = "react"
        state = "open"
        per_page = 5
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "http://localhost:8102/list_issues" -Method POST -Headers $headers -Body $issueBody
    Write-Host "   ✓ Found $($result.Count) open issues" -ForegroundColor Green
    if ($result.Count -gt 0) {
        Write-Host "   ✓ Latest issue: #$($result[0].number) - $($result[0].title)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ✗ Issue listing failed: $_" -ForegroundColor Red
}

Write-Host "`n✅ Test Complete!" -ForegroundColor Green
Write-Host "`nTo test CREATE operations, use the prompts in OpenWebUI chat." -ForegroundColor Cyan
Write-Host "This avoids creating test data in public repositories." -ForegroundColor Yellow
