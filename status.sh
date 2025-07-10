#!/bin/bash

# Mac Status Script for OpenWebUI + MCP Tools
# Equivalent to status.bat but for macOS/Linux

echo "📊 OpenWebUI + MCP Tools Status (Mac Version)"
echo "=============================================="

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
else
    echo "✅ Docker is running"
fi

echo ""
echo "🐳 Container Status:"
docker-compose -f docker-compose.local.yml ps

echo ""
echo "🌐 Service Health Check:"

# Function to test endpoint
test_endpoint() {
    local name=$1
    local port=$2
    local path=${3:-"/health"}
    
    if curl -s "http://localhost:$port$path" > /dev/null 2>&1; then
        echo "   ✅ $name (port $port) - OK"
    else
        echo "   ❌ $name (port $port) - FAILED"
    fi
}

test_endpoint "OpenWebUI" "8080" ""
test_endpoint "GitHub Tools" "8102" "/openapi.json"
test_endpoint "Filesystem Tools" "8103" "/openapi.json"
test_endpoint "Brave Search" "8104" "/openapi.json"
test_endpoint "Memory Tools" "8105" "/openapi.json"

echo ""
echo "💾 Data Usage:"
if [ -d "data/workspace" ]; then
    echo "   📁 Workspace: $(du -sh data/workspace 2>/dev/null | cut -f1)"
fi
if [ -d "data/openwebui" ]; then
    echo "   📱 OpenWebUI: $(du -sh data/openwebui 2>/dev/null | cut -f1)"
fi 