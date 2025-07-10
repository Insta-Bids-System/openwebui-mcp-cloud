#!/bin/bash

# Stop Enhanced MCP Setup

echo "🛑 Stopping Enhanced MCP Setup..."

# Stop all services
docker-compose -f docker-compose.enhanced.yml down

echo "✅ All Enhanced MCP services stopped" 