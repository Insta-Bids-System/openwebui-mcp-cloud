#!/bin/bash

# Mac GitHub MCP Tools Test Script
# Equivalent to test-github-tools.ps1 but for macOS/Linux

echo "🔧 Testing GitHub MCP Tools Setup (Mac Version)"
echo "================================================"

# Test 1: Check if MCPO is running
echo ""
echo "1. Checking MCPO GitHub Server..."
if curl -s "http://localhost:8102/openapi.json" > /dev/null; then
    echo "   ✅ MCPO server is running"
else
    echo "   ❌ MCPO server is not accessible"
    echo "   💡 Run ./start.sh to start services"
    exit 1
fi

# Test 2: List available tools
echo ""
echo "2. Available GitHub Tools:"
curl -s "http://localhost:8102/openapi.json" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
tools = list(data.get('paths', {}).keys())
for i, tool in enumerate(tools[:10]):
    print(f'   - {tool}')
if len(tools) > 10:
    print(f'   ... and {len(tools) - 10} more tools')
" 2>/dev/null || echo "   ❌ Could not retrieve tool list"

# Test 3: Test authentication
echo ""
echo "3. Testing Authentication..."
response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8102/list_repositories" \
    -H "Authorization: Bearer local-mcp-key-for-testing" \
    -H "Content-Type: application/json" \
    -d '{}' -o /tmp/github_response.json)

if [ "$response" = "200" ]; then
    echo "   ✅ Authentication successful"
    # Try to count repositories if response is valid JSON
    python3 -c "
import json
try:
    with open('/tmp/github_response.json') as f:
        data = json.load(f)
    repos = data.get('repositories', [])
    print(f'   ✅ Found {len(repos)} repositories')
except:
    print('   ✅ Response received')
" 2>/dev/null
else
    echo "   ❌ Authentication failed (HTTP $response)"
fi

# Test 4: Test search functionality
echo ""
echo "4. Testing Repository Search..."
search_response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8102/search_repositories" \
    -H "Authorization: Bearer local-mcp-key-for-testing" \
    -H "Content-Type: application/json" \
    -d '{"query": "language:python stars:>100"}' -o /tmp/search_response.json)

if [ "$search_response" = "200" ]; then
    echo "   ✅ Search functionality working"
    python3 -c "
import json
try:
    with open('/tmp/search_response.json') as f:
        data = json.load(f)
    total = data.get('total_count', 0)
    print(f'   ✅ Found {total} Python repositories with 100+ stars')
except:
    print('   ✅ Search completed')
" 2>/dev/null
else
    echo "   ❌ Search failed (HTTP $search_response)"
fi

echo ""
echo "🎯 Next Steps:"
echo "   1. Open http://localhost:8080 in your browser"
echo "   2. Go to Settings → Tools"
echo "   3. Add new tool with:"
echo "      - API Base URL: http://localhost:8102"
echo "      - Bearer Token: local-mcp-key-for-testing"
echo "      - Auto-append /openapi.json: ON"

# Cleanup temp files
rm -f /tmp/github_response.json /tmp/search_response.json 