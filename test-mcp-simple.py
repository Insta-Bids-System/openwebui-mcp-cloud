#!/usr/bin/env python3
"""
Simple test script for the MCP HTTP server
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8101"
API_KEY = "local-mcp-key-for-testing"

print("Testing MCP HTTP Server")
print(f"Server: {BASE_URL}")
print("=" * 50)

# Test health endpoint
print("\n1. Testing Health Endpoint (No Auth)")
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("SUCCESS: Health check passed")
        print(f"Response: {response.json()}")
    else:
        print(f"FAILED: Health check failed: {response.status_code}")
except Exception as e:
    print(f"ERROR: Connection error: {e}")
    print("Is the server running?")
    exit(1)

# Test OpenAPI endpoint
print("\n2. Testing OpenAPI Documentation")
try:
    response = requests.get(f"{BASE_URL}/openapi.json")
    if response.status_code == 200:
        schema = response.json()
        print("SUCCESS: OpenAPI schema retrieved")
        print(f"Title: {schema.get('info', {}).get('title')}")
        print(f"Version: {schema.get('info', {}).get('version')}")
        print(f"Endpoints: {len(schema.get('paths', {}))}")
    else:
        print(f"FAILED: OpenAPI retrieval failed: {response.status_code}")
except Exception as e:
    print(f"ERROR: {e}")

# Test authenticated endpoint
print("\n3. Testing Authenticated Endpoint (App Config)")
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
try:
    response = requests.get(f"{BASE_URL}/tools/get_app_config", headers=headers)
    if response.status_code == 200:
        print("SUCCESS: Authenticated request successful")
        result = response.json()
        print(f"Response preview: {str(result)[:100]}...")
    else:
        print(f"FAILED: Status {response.status_code}")
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 50)
print("Test complete! MCP HTTP server is working.")
print("\nNext steps:")
print("1. Add the server to OpenWebUI at Settings -> Tools")
print(f"   - URL: {BASE_URL}")
print(f"   - Token: {API_KEY}")
print("2. Try in chat: 'List all users in OpenWebUI'")
