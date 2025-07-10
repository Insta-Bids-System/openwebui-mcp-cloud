#!/usr/bin/env python3
"""
Test script for the fixed MCP HTTP server
Tests basic functionality of the OpenWebUI management tools
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8101"
API_KEY = "local-mcp-api-key"  # Change this to match your MCP_API_KEY

def test_endpoint(name, method, path, data=None):
    """Test a single endpoint"""
    print(f"\n🔍 Testing {name}...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{path}", headers=headers)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{path}", headers=headers, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == 200:
            print(f"✅ Success: {response.status_code}")
            result = response.json()
            print(f"📋 Response: {json.dumps(result, indent=2)[:200]}...")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"📋 Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing MCP HTTP Server")
    print(f"📍 Server: {BASE_URL}")
    print(f"🔑 API Key: {API_KEY[:10]}...")
    print(f"🕐 Time: {datetime.now()}")
    
    # Test health endpoint (no auth required)
    print("\n" + "="*50)
    print("1️⃣ Testing Health Endpoint (No Auth)")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"📋 Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\n⚠️  Is the server running? Try:")
        print("   docker-compose -f docker-compose.mcp-http.yml up -d")
        sys.exit(1)
    
    # Test OpenAPI endpoint
    print("\n" + "="*50)
    print("2️⃣ Testing OpenAPI Documentation")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            print(f"✅ OpenAPI schema retrieved")
            print(f"📋 Title: {schema.get('info', {}).get('title')}")
            print(f"📋 Version: {schema.get('info', {}).get('version')}")
            print(f"📋 Endpoints: {len(schema.get('paths', {}))}")
        else:
            print(f"❌ OpenAPI retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test authenticated endpoints
    print("\n" + "="*50)
    print("3️⃣ Testing Authenticated Endpoints")
    
    tests = [
        ("App Config", "GET", "/tools/get_app_config"),
        ("App Version", "GET", "/tools/get_app_version"),
        ("List Users", "GET", "/tools/list_users"),
        ("List Models", "GET", "/tools/list_models"),
        ("List Chats", "GET", "/tools/list_chats?limit=5"),
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test_endpoint(*test):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! The MCP HTTP server is working correctly.")
        print("\n📌 Next steps:")
        print("1. Add the server to OpenWebUI:")
        print(f"   - URL: {BASE_URL}")
        print(f"   - Token: {API_KEY}")
        print("2. Try in chat: 'List all users in OpenWebUI'")
    else:
        print("\n⚠️  Some tests failed. Check the server logs:")
        print("   docker logs -f local-mcp-server-http")

if __name__ == "__main__":
    main()
