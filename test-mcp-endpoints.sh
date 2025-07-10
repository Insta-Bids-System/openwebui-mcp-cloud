#!/bin/bash

# Mac MCP Endpoints Test Script
# Equivalent to test-mcp-endpoints.ps1 but for macOS/Linux

echo "🔧 Testing All MCP Endpoints (Mac Version)"
echo "=========================================="

# Function to test endpoint
test_mcp_endpoint() {
    local name=$1
    local port=$2
    local test_path=${3:-"/openapi.json"}
    
    echo ""
    echo "Testing $name (Port $port)..."
    
    local response=$(curl -s -w "%{http_code}" "http://localhost:$port$test_path" -o /tmp/mcp_test.json)
    
    if [ "$response" = "200" ]; then
        local tool_count=$(python3 -c "
import json
try:
    with open('/tmp/mcp_test.json') as f:
        data = json.load(f)
    paths = data.get('paths', {})
    print(len(paths))
except:
    print(0)
" 2>/dev/null || echo "0")
        
        echo "   ✅ SUCCESS: $tool_count tools available"
        
        if [ "$tool_count" -gt 0 ]; then
            echo "   Sample tools:"
            python3 -c "
import json
try:
    with open('/tmp/mcp_test.json') as f:
        data = json.load(f)
    tools = list(data.get('paths', {}).keys())
    for tool in tools[:5]:
        print(f'   - {tool}')
except:
    pass
" 2>/dev/null
        fi
    else
        echo "   ❌ FAILED: HTTP $response"
        echo "   💡 Check logs: docker logs local-mcpo-$(echo $name | tr '[:upper:]' '[:lower:]')"
    fi
}

# Test each service
test_mcp_endpoint "OpenWebUI" "8101"
test_mcp_endpoint "GitHub" "8102"
test_mcp_endpoint "Filesystem" "8103"
test_mcp_endpoint "Brave-Search" "8104"
test_mcp_endpoint "Memory" "8105"

echo ""
echo "=========================================="
echo "🎯 Test Complete"
echo "=========================================="

# Test specific tool execution
echo ""
echo "Testing tool execution (OpenWebUI health check)..."

health_response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8101/get_app_config" \
    -H "Authorization: Bearer local-mcp-api-key" \
    -H "Content-Type: application/json" \
    -d '{}' -o /tmp/health_test.json)

if [ "$health_response" = "200" ]; then
    echo "   ✅ Tool execution working"
else
    echo "   ❌ Tool execution failed (HTTP $health_response)"
fi

echo ""
echo "📚 All MCP Services Summary:"
echo "   • OpenWebUI Tools:  http://localhost:8101"
echo "   • GitHub Tools:     http://localhost:8102"
echo "   • Filesystem Tools: http://localhost:8103"
echo "   • Brave Search:     http://localhost:8104"
echo "   • Memory Tools:     http://localhost:8105"

# Cleanup
rm -f /tmp/mcp_test.json /tmp/health_test.json 