#!/bin/bash

# Test Filesystem Wrapper

echo "🧪 Testing Filesystem Wrapper..."

# Check if wrapper is running
if ! curl -s -f http://localhost:8107/openapi.json > /dev/null; then
    echo "❌ Filesystem wrapper not running on port 8107"
    echo "Run: ./start-enhanced.sh"
    exit 1
fi

echo "✅ Filesystem wrapper is running"

# Test path normalization
echo ""
echo "🔧 Testing path normalization..."

# Test 1: Current directory "."
echo "Test 1: Converting '.' to '/workspace'"
response=$(curl -s -X POST "http://localhost:8107/list_directory" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer local-mcp-key-for-testing" \
    -d '{"path": "."}')

if echo "$response" | grep -q "workspace"; then
    echo "✅ Path '.' converted to '/workspace'"
else
    echo "❌ Path normalization failed"
    echo "Response: $response"
fi

# Test 2: Relative path
echo ""
echo "Test 2: Converting 'test.txt' to '/workspace/test.txt'"
response=$(curl -s -X POST "http://localhost:8107/read_file" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer local-mcp-key-for-testing" \
    -d '{"path": "test.txt"}')

# Check logs for path conversion (wrapper should log the transformation)
echo "✅ Test completed - check wrapper logs for path conversion"

echo ""
echo "🔍 View detailed logs with:"
echo "docker-compose -f docker-compose.enhanced.yml logs filesystem-wrapper" 