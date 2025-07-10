#!/usr/bin/env python3
"""
Test GitHub MCP Tools with Gemini
Demonstrates how AI can interact with working MCP GitHub tools
"""

import requests
import json
import os
from datetime import datetime

# Configuration
GITHUB_MCP_URL = "http://localhost:8102"
MCP_API_KEY = "local-mcp-key-for-testing"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# MCP Headers
MCP_HEADERS = {
    "Authorization": f"Bearer {MCP_API_KEY}",
    "Content-Type": "application/json"
}

def test_mcp_github_tools():
    """Test various GitHub MCP tools and return results"""
    
    print("🔍 Testing GitHub MCP Tools...")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Search repositories (this works)
    print("1. Testing search_repositories...")
    try:
        response = requests.post(
            f"{GITHUB_MCP_URL}/search_repositories",
            headers=MCP_HEADERS,
            json={"query": "openwebui stars:>10", "page": 1, "perPage": 3}
        )
        if response.status_code == 200:
            data = response.json()
            results["search"] = {
                "status": "✅ SUCCESS", 
                "total": data.get("total_count", 0),
                "repos": [repo.get("full_name", "Unknown") for repo in data.get("items", [])[:3]]
            }
            print(f"   ✅ Found {data.get('total_count', 0)} repositories")
        else:
            results["search"] = {"status": "❌ FAILED", "error": response.text}
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        results["search"] = {"status": "❌ ERROR", "error": str(e)}
        print(f"   ❌ Error: {e}")
    
    # Test 2: List repositories (this fails - "your_username" bug)
    print("\n2. Testing list_repositories...")
    try:
        response = requests.post(
            f"{GITHUB_MCP_URL}/list_repositories",
            headers=MCP_HEADERS,
            json={}
        )
        if response.status_code == 200:
            data = response.json()
            results["list"] = {"status": "✅ SUCCESS", "count": len(data)}
            print(f"   ✅ Listed {len(data)} repositories")
        else:
            results["list"] = {"status": "❌ FAILED", "error": response.text}
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        results["list"] = {"status": "❌ ERROR", "error": str(e)}
        print(f"   ❌ Error: {e}")
    
    # Test 3: Search code (this should work)
    print("\n3. Testing search_code...")
    try:
        response = requests.post(
            f"{GITHUB_MCP_URL}/search_code",
            headers=MCP_HEADERS,
            json={"q": "openwebui language:python", "page": 1, "per_page": 3}
        )
        if response.status_code == 200:
            data = response.json()
            results["code_search"] = {
                "status": "✅ SUCCESS",
                "total": data.get("total_count", 0),
                "files": [item.get("name", "Unknown") for item in data.get("items", [])[:3]]
            }
            print(f"   ✅ Found {data.get('total_count', 0)} code files")
        else:
            results["code_search"] = {"status": "❌ FAILED", "error": response.text}
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        results["code_search"] = {"status": "❌ ERROR", "error": str(e)}
        print(f"   ❌ Error: {e}")
    
    return results

def analyze_with_gemini(results):
    """Use Gemini to analyze the MCP test results"""
    
    if not GEMINI_API_KEY:
        print("\n⚠️  GEMINI_API_KEY not set - skipping AI analysis")
        print("   Set GEMINI_API_KEY in your .env file to enable Gemini integration")
        return
    
    print("\n🤖 Analyzing results with Gemini...")
    print("=" * 50)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
Analyze these GitHub MCP tool test results and provide insights:

Test Results:
{json.dumps(results, indent=2)}

Please provide:
1. Summary of what's working vs broken
2. Analysis of the patterns you see
3. Recommendations for next steps
4. Overall assessment of the MCP GitHub integration

Format your response in a clear, structured way.
"""
        
        response = model.generate_content(prompt)
        print(response.text)
        
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Install with: pip install google-generativeai")
    except Exception as e:
        print(f"❌ Gemini analysis failed: {e}")

def simulate_ai_github_workflow():
    """Simulate an AI workflow using working GitHub MCP tools"""
    
    print("\n🚀 Simulating AI-Powered GitHub Workflow...")
    print("=" * 50)
    
    # Step 1: Search for repositories
    print("1. AI asks: 'Find popular OpenWebUI repositories'")
    try:
        response = requests.post(
            f"{GITHUB_MCP_URL}/search_repositories",
            headers=MCP_HEADERS,
            json={"query": "openwebui stars:>5", "page": 1, "perPage": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            repos = data.get("items", [])[:3]
            
            print(f"   🤖 AI found {data.get('total_count', 0)} repositories!")
            for repo in repos:
                print(f"      • {repo.get('full_name')} ({repo.get('stargazers_count', 0)} ⭐)")
            
            # Step 2: Try to get file contents from first repo
            if repos:
                first_repo = repos[0]
                owner, repo_name = first_repo["full_name"].split("/")
                
                print(f"\n2. AI asks: 'Get README from {first_repo['full_name']}'")
                file_response = requests.post(
                    f"{GITHUB_MCP_URL}/get_file_contents",
                    headers=MCP_HEADERS,
                    json={"owner": owner, "repo": repo_name, "path": "README.md"}
                )
                
                if file_response.status_code == 200:
                    file_data = file_response.json()
                    content = file_data.get("content", "")[:200]
                    print(f"   ✅ AI successfully read README content:")
                    print(f"      📄 Content preview: {content}...")
                else:
                    print(f"   ❌ AI couldn't read README: {file_response.status_code}")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Workflow failed: {e}")

def main():
    """Main test function"""
    
    print("🧪 GitHub MCP Tools + Gemini Integration Test")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 MCP Endpoint: {GITHUB_MCP_URL}")
    print(f"🤖 Gemini API: {'✅ Configured' if GEMINI_API_KEY else '❌ Not configured'}")
    print()
    
    # Test MCP tools
    results = test_mcp_github_tools()
    
    # Analyze with Gemini (if available)
    analyze_with_gemini(results)
    
    # Simulate AI workflow
    simulate_ai_github_workflow()
    
    print("\n📊 Summary:")
    print("=" * 30)
    working_tools = [k for k, v in results.items() if "SUCCESS" in v.get("status", "")]
    broken_tools = [k for k, v in results.items() if "SUCCESS" not in v.get("status", "")]
    
    print(f"✅ Working tools: {len(working_tools)} ({', '.join(working_tools)})")
    print(f"❌ Broken tools: {len(broken_tools)} ({', '.join(broken_tools)})")
    print()
    print("🎯 Next Steps:")
    print("   1. Fix the 'your_username' bug in broken tools")
    print("   2. Configure OpenWebUI to use these MCP tools")
    print("   3. Test full integration with AI models")

if __name__ == "__main__":
    main() 