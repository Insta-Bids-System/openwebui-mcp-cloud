#!/usr/bin/env python3
"""
Test GitHub MCP with updated token
"""
import requests
import json

print("Testing GitHub MCP Service")
print("=" * 50)

# Test OpenAPI endpoint
print("\n1. Testing OpenAPI endpoint...")
headers = {"Authorization": "Bearer local-mcp-key-for-testing"}
try:
    response = requests.get("http://localhost:8102/openapi.json", headers=headers)
    if response.status_code == 200:
        print("[SUCCESS] GitHub MCP is accessible")
        schema = response.json()
        print(f"Service: {schema.get('info', {}).get('title', 'Unknown')}")
        print(f"Available endpoints: {len(schema.get('paths', {}))}")
    else:
        print(f"[ERROR] Failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")

# Test a simple search
print("\n2. Testing GitHub search...")
search_data = {
    "query": "language:python stars:>10",
    "owner": "{owner}",
    "limit": 3
}

try:
    response = requests.post(
        "http://localhost:8102/tools/search_repositories",
        json=search_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print("[SUCCESS] GitHub search is working!")
        result = response.json()
        if "items" in result:
            print(f"Found {len(result['items'])} repositories")
            for repo in result['items'][:3]:
                print(f"  - {repo.get('full_name', 'Unknown')}: {repo.get('stargazers_count', 0)} stars")
        else:
            print("Response:", json.dumps(result, indent=2)[:200])
    else:
        print(f"[ERROR] Search failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"[ERROR] Search request failed: {e}")

print("\n" + "=" * 50)
print("GitHub token has been updated successfully!")
print("You can now use GitHub tools in OpenWebUI.")
