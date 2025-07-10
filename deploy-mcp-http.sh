#!/bin/bash

# Deploy the fixed MCP server with HTTP integration
# This bypasses MCPO's stdio issues with Python MCP servers

echo "🚀 Deploying fixed MCP server with HTTP integration..."

# Check if we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found. Please run from project root."
    exit 1
fi

# Stop any existing MCP server containers
echo "🛑 Stopping any existing MCP server..."
docker-compose -f docker-compose.mcp-only.yml stop mcpo-openwebui 2>/dev/null
docker-compose -f docker-compose.mcp-only.yml rm -f mcpo-openwebui 2>/dev/null

# Build the new HTTP server
echo "🔨 Building MCP HTTP server..."
docker-compose -f docker-compose.mcp-http.yml build

# Start the HTTP server
echo "🚀 Starting MCP HTTP server..."
docker-compose -f docker-compose.mcp-http.yml up -d

# Wait for it to be ready
echo "⏳ Waiting for server to be ready..."
sleep 10

# Test the health endpoint
echo "🔍 Testing health endpoint..."
curl -s http://localhost:8101/health | jq .

# Test the OpenAPI endpoint
echo "📋 Checking OpenAPI endpoint..."
curl -s http://localhost:8101/openapi.json | jq '.info'

echo ""
echo "✅ MCP HTTP server deployed!"
echo ""
echo "📌 Next steps:"
echo "1. Add to OpenWebUI at Settings → Tools"
echo "   - API Base URL: http://localhost:8101"
echo "   - Bearer Token: ${MCP_API_KEY:-local-mcp-api-key}"
echo "   - Enable 'Auto-append /openapi.json'"
echo ""
echo "2. Test with: 'List all users in OpenWebUI'"
echo ""
echo "3. View logs: docker logs -f local-mcp-server-http"
