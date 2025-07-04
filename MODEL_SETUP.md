# 🤖 Model Configuration Guide

## Option 1: OpenAI (Recommended for Testing)

1. Go to Settings → Connections
2. Click on "OpenAI"
3. Enter your OpenAI API key
4. Click "Save"
5. Models like GPT-3.5 and GPT-4 will appear

## Option 2: Anthropic (Claude)

1. Go to Settings → Connections  
2. Click on "Anthropic"
3. Enter your Anthropic API key
4. Click "Save"
5. Claude models will appear

## Option 3: Local Ollama (Free)

1. Install Ollama: https://ollama.ai
2. Run: `ollama pull llama2` (or any model)
3. In OpenWebUI Settings → Connections
4. Ollama should auto-detect at http://localhost:11434
5. Local models will appear

## Option 4: Custom OpenAI-Compatible

1. Settings → Connections → OpenAI-Compatible
2. Enter your endpoint URL
3. Enter API key if required
4. Save and test

## Selecting a Model

After configuring:
1. Go to main chat interface
2. Click model selector (top of chat)
3. Choose your model
4. Start chatting!

## No API Key?

For free testing:
- Use Ollama (completely local)
- Get free OpenAI credits: https://platform.openai.com
- Get Anthropic API: https://console.anthropic.com