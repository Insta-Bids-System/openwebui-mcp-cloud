#!/usr/bin/env python3
"""
Quick GitHub token verification script
"""
import os
import urllib.request
import urllib.error
import json

def check_github_token():
    # Read token from .env.local
    token = None
    try:
        with open('.env.local', 'r') as f:
            for line in f:
                if line.startswith('GITHUB_TOKEN='):
                    token = line.split('=', 1)[1].strip()
                    break
    except Exception as e:
        print(f"Error reading .env.local: {e}")
        return
    
    if not token:
        print("[ERROR] No GitHub token found in .env.local")
        return
    
    if "REPLACE THIS" in token or token == "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":
        print("[ERROR] You're still using the placeholder token!")
        print("   Please replace it with your actual GitHub token")
        return
    
    # Test the token
    print(f"[INFO] Testing GitHub token: {token[:10]}...")
    
    try:
        req = urllib.request.Request('https://api.github.com/user')
        req.add_header('Authorization', f'token {token}')
        req.add_header('Accept', 'application/vnd.github.v3+json')
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"[SUCCESS] Token is valid! Authenticated as: {data.get('login', 'Unknown')}")
            print(f"   Name: {data.get('name', 'Not set')}")
            print(f"   Email: {data.get('email', 'Not set')}")
            return True
            
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("[ERROR] Invalid token! The token is not authorized.")
        elif e.code == 403:
            print("[ERROR] Token might be valid but lacks required permissions.")
        else:
            print(f"[ERROR] HTTP Error {e.code}: {e.reason}")
    except Exception as e:
        print(f"[ERROR] Error testing token: {e}")
    
    return False

if __name__ == "__main__":
    print("GitHub Token Verification")
    print("=" * 50)
    
    if check_github_token():
        print("\n[SUCCESS] Your GitHub token is working correctly!")
        print("\nNow restart the GitHub MCP service:")
        print("docker-compose -f docker-compose.local.yml restart mcpo-github")
    else:
        print("\n[ERROR] Please update your GitHub token in .env.local")
        print("\nGet a new token at: https://github.com/settings/tokens/new")
        print("Required scopes: repo, read:user, user:email")
