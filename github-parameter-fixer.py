#!/usr/bin/env python3
"""
GitHub Parameter Fixer - Proxy Server
Intercepts GitHub MCP calls and fixes the owner parameter automatically
"""

from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Configuration
GITHUB_MCP_SERVER = "http://localhost:8102"
CORRECT_OWNER = "Insta-Bids-System"
API_KEY = "local-mcp-key-for-testing"

# Operations that need owner parameter fixed
CRUD_OPERATIONS = [
    "create_or_update_file",
    "create_repository", 
    "get_file_contents",
    "push_files"
]

def fix_github_parameters(data, operation):
    """Fix GitHub parameters by ensuring correct owner"""
    if not data:
        return data
        
    # Only fix CRUD operations
    if operation in CRUD_OPERATIONS:
        # If owner exists and looks like a repo name, fix it
        if "owner" in data:
            # Common repo name patterns that are wrong
            repo_patterns = [
                "openwebui-mcp-test",
                "mcp-test", 
                "new-project",
                "my-project"
            ]
            
            # If owner matches a repo pattern or is same as repo, fix it
            if (data["owner"] in repo_patterns or 
                data["owner"] == data.get("repo", "")):
                print(f"🔧 FIXING: Changed owner from '{data['owner']}' to '{CORRECT_OWNER}'")
                data["owner"] = CORRECT_OWNER
                
        # If no owner but this is a CRUD operation, add it
        elif operation in CRUD_OPERATIONS:
            print(f"🔧 ADDING: Owner '{CORRECT_OWNER}' for {operation}")
            data["owner"] = CORRECT_OWNER
            
    return data

@app.route('/<operation>', methods=['POST'])
def proxy_github_operation(operation):
    """Proxy GitHub operations with parameter fixing"""
    try:
        # Get original request data
        data = request.get_json() or {}
        
        # Fix parameters if needed
        fixed_data = fix_github_parameters(data.copy(), operation)
        
        # Log the fix if parameters changed
        if fixed_data != data:
            print(f"📝 Original: {json.dumps(data, indent=2)}")
            print(f"✅ Fixed:    {json.dumps(fixed_data, indent=2)}")
        
        # Forward to real GitHub MCP server
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{GITHUB_MCP_SERVER}/{operation}",
            json=fixed_data,
            headers=headers
        )
        
        # Return the response
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        print(f"❌ Error in proxy: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "GitHub Parameter Fixer is running"})

if __name__ == "__main__":
    print("🚀 Starting GitHub Parameter Fixer Proxy...")
    print(f"📡 Proxying to: {GITHUB_MCP_SERVER}")
    print(f"🔧 Auto-fixing owner to: {CORRECT_OWNER}")
    print("🌐 Running on: http://localhost:8106")
    
    app.run(host="0.0.0.0", port=8106, debug=True) 