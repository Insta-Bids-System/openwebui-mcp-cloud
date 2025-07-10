#!/usr/bin/env python3
"""
Test LiteLLM proxy configuration
"""
import requests
import json

LITELLM_URL = "http://localhost:4000"

print("Testing LiteLLM Proxy Configuration")
print("=" * 50)

# Test health endpoint
print("\n1. Testing Health Endpoint")
try:
    response = requests.get(f"{LITELLM_URL}/health")
    if response.status_code == 200:
        print("[SUCCESS] LiteLLM is running")
    else:
        print(f"[ERROR] Health check failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] Cannot connect to LiteLLM: {e}")
    print("Is LiteLLM running? Try: docker ps | grep litellm")
    exit(1)

# Test models endpoint
print("\n2. Testing Available Models")
try:
    response = requests.get(f"{LITELLM_URL}/v1/models")
    if response.status_code == 200:
        models = response.json()
        print(f"[SUCCESS] Found {len(models.get('data', []))} models:")
        for model in models.get('data', []):
            print(f"  - {model.get('id', 'unknown')}")
    else:
        print(f"[ERROR] Models endpoint failed: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"[ERROR] Failed to get models: {e}")

# Instructions
print("\n" + "=" * 50)
print("Configuration Instructions:")
print("\n1. Make sure you have API keys in .env.local:")
print("   OPENAI_API_KEY=sk-...")
print("   GEMINI_API_KEY=...")
print("\n2. In OpenWebUI Settings -> Connections:")
print("   - Remove Ollama connections")
print("   - Add OpenAI API:")
print("     * Base URL: http://localhost:4000/v1")
print("     * API Key: any-string-here")
print("\n3. Refresh OpenWebUI and select a GPT model")
