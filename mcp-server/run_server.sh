#!/bin/bash
# Install dependencies if not already installed
pip install mcp fastmcp aiohttp redis asyncio urllib3 2>/dev/null || true

# Run the MCP server
cd /mcp-server && python main.py
