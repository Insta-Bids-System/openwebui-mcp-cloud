#!/bin/bash

echo "🚀 Starting Simple OpenWebUI MCP Setup (Ports 8101 & 8102)"
echo "=========================================================="

# Start the services
docker-compose -f docker-compose.simple-rollback.yml up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "✅ Setup complete! Running status check..."
echo ""

# Run status check
./check-simple-setup.sh 