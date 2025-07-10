# 🔧 Fix OpenWebUI Model Configuration

## Problem
OpenWebUI is trying to connect to Ollama models instead of GPT models through LiteLLM.

## Quick Fix

### Step 1: Add Your API Keys to `.env.local`

Add these lines to your `.env.local` file:

```env
# OpenAI API Key (for GPT models)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE

# Gemini API Key (optional, for Gemini models)
# Get from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

### Step 2: Update LiteLLM Configuration

Create a new file `litellm-config.yaml`:

```yaml
model_list:
  # GPT-4 Models
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: ${OPENAI_API_KEY}
      
  - model_name: gpt-4-turbo
    litellm_params:
      model: openai/gpt-4-turbo-preview
      api_key: ${OPENAI_API_KEY}
      
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
      
  # Gemini Models (if you have API key)
  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-pro
      api_key: ${GEMINI_API_KEY}

litellm_settings:
  drop_params: false
  set_verbose: true
```

### Step 3: Update docker-compose.local.yml

Replace the litellm service with:

```yaml
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: local-litellm
    ports:
      - "4000:4000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./litellm-config.yaml:/app/config.yaml
    command: [
      "--config", "/app/config.yaml",
      "--port", "4000"
    ]
    networks:
      - local-ai-net
```

### Step 4: Configure OpenWebUI to Use LiteLLM

1. Go to **Settings → Connections** in OpenWebUI
2. Remove any Ollama connections
3. Add **OpenAI API** connection:
   - API Base URL: `http://localhost:4000/v1`
   - API Key: `any-string-here` (LiteLLM handles the real keys)

### Step 5: Restart Services

```bash
# Stop everything
docker-compose -f docker-compose.local.yml down

# Start with new configuration
docker-compose -f docker-compose.local.yml up -d

# Wait 30 seconds for services to start
# Then refresh OpenWebUI
```

## Alternative: Direct OpenAI Connection

If you prefer to connect directly to OpenAI without LiteLLM:

1. In OpenWebUI, go to **Settings → Connections**
2. Add **OpenAI API**:
   - API Base URL: `https://api.openai.com/v1`
   - API Key: `sk-YOUR_OPENAI_API_KEY_HERE`

## Verification

After configuration:
1. Refresh OpenWebUI (F5)
2. Click model selector
3. You should see GPT models listed
4. Select a GPT model and test with "Hello"

## Troubleshooting

If models don't appear:
- Check docker logs: `docker logs local-litellm`
- Verify API keys are correct
- Ensure LiteLLM is running: `docker ps | grep litellm`
- Clear browser cache and cookies for localhost:8080
