#!/bin/bash

# Mac Stop Script for OpenWebUI + MCP Tools
# Equivalent to stop.bat but for macOS/Linux

echo "🛑 Stopping OpenWebUI + MCP Tools (Mac Version)"
echo "=============================================="

# Stop all services
echo "🐳 Stopping Docker services..."
docker-compose -f docker-compose.local.yml down

echo ""
echo "✅ All services stopped successfully!"
echo ""
echo "💡 Data is preserved in ./data/ directory"
echo "💡 To start again: ./start.sh" 