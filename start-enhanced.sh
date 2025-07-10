#!/bin/bash

# Enhanced MCP Setup with Both Wrappers
# This starts GitHub wrapper (port 8102) and Filesystem wrapper (port 8107)

set -e

echo "🚀 Starting Enhanced MCP Setup with Both Wrappers..."

# Check prerequisites
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cat > .env << EOF
GITHUB_TOKEN=your_github_token_here
BRAVE_SEARCH_API_KEY=your_brave_search_key_here
EOF
    echo "📝 Please edit .env with your API keys"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '#' | xargs)

# Validate GitHub token
if [ "$GITHUB_TOKEN" = "your_github_token_here" ]; then
    echo "❌ Please set your GITHUB_TOKEN in .env file"
    exit 1
fi

# Create workspace directory
mkdir -p ./data/workspace
echo "📁 Workspace directory created: ./data/workspace"

# Start services
echo "🐳 Starting enhanced MCP services..."
docker-compose -f docker-compose.enhanced.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Health checks
echo "🏥 Performing health checks..."

services=(
    "GitHub Wrapper:http://localhost:8102/openapi.json"
    "Filesystem Wrapper:http://localhost:8107/openapi.json"
    "Filesystem MCP:http://localhost:8104/openapi.json"
    "Search MCP:http://localhost:8105/openapi.json"
    "Memory MCP:http://localhost:8106/openapi.json"
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    url=$(echo $service | cut -d: -f2,3)
    
    if curl -s -f "$url" > /dev/null; then
        echo "✅ $name - OK"
    else
        echo "❌ $name - FAILED"
    fi
done

echo ""
echo "🎉 Enhanced MCP Setup Complete!"
echo ""
echo "📋 Service URLs:"
echo "   GitHub Wrapper (Enhanced):  http://localhost:8102"
echo "   Filesystem Wrapper (Enhanced): http://localhost:8107"
echo "   Filesystem MCP (Direct):    http://localhost:8104"
echo "   Search MCP:                 http://localhost:8105"
echo "   Memory MCP:                 http://localhost:8106"
echo ""
echo "🔧 OpenWebUI Configuration:"
echo "   1. Go to Settings > Tools"
echo "   2. Add these MCP servers:"
echo "      - GitHub (Enhanced): http://localhost:8102"
echo "      - Filesystem (Enhanced): http://localhost:8107"
echo "      - Search: http://localhost:8105"
echo "      - Memory: http://localhost:8106"
echo ""
echo "✨ Benefits:"
echo "   - GitHub: Auto-injects 'Insta-Bids-System' as owner"
echo "   - Filesystem: Auto-converts '.' to '/workspace'"
echo "   - Both: Intelligent tool redirection and error handling"
echo ""
echo "🔍 Monitor logs with:"
echo "   docker-compose -f docker-compose.enhanced.yml logs -f" 