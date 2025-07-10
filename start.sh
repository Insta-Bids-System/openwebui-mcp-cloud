#!/bin/bash

# Mac Start Script for OpenWebUI + MCP Tools
# Equivalent to start.bat but for macOS/Linux

echo "🚀 Starting OpenWebUI + MCP Tools (Mac Version)"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if .env.mac exists
if [ ! -f ".env.mac" ]; then
    echo "❌ .env.mac file not found. Please create it first."
    exit 1
fi

# Copy .env.mac to .env for docker-compose
cp .env.mac .env
echo "✅ Environment file loaded"

# Create data directories
mkdir -p data/workspace
mkdir -p data/openwebui
mkdir -p data/memory
echo "✅ Data directories created"

# Start services
echo "🐳 Starting Docker services..."
docker-compose -f docker-compose.local.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose -f docker-compose.local.yml ps

echo ""
echo "🎉 OpenWebUI + MCP Tools started successfully!"
echo ""
echo "📱 Access URLs:"
echo "   • OpenWebUI:      http://localhost:8080"
echo "   • GitHub Tools:   http://localhost:8102"
echo "   • Filesystem:     http://localhost:8103"
echo "   • Brave Search:   http://localhost:8104"
echo "   • Memory Tools:   http://localhost:8105"
echo ""
echo "🔧 Next Steps:"
echo "   1. Open http://localhost:8080 in your browser"
echo "   2. Create admin account"
echo "   3. Go to Settings → Tools and add the MCP endpoints"
echo ""
echo "💡 To stop: ./stop.sh"
echo "💡 To check status: ./status.sh" 