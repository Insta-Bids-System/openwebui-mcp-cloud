#!/bin/bash

echo "🛑 Stopping Simple OpenWebUI MCP Setup"
echo "======================================"

# Stop the services
docker-compose -f docker-compose.simple-rollback.yml down

echo ""
echo "✅ All services stopped successfully!" 