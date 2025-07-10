# LiteLLM Configuration for Multiple Models

## Quick Setup:

1. **Stop current LiteLLM:**
   ```bash
   docker stop local-litellm
   docker rm local-litellm
   ```

2. **Create LiteLLM config file:**

Save this as `litellm-config.yaml`:

```yaml
model_list:
  - model_name: gemini-flash
    litellm_params:
      model: gemini/gemini-1.5-flash
      api_key: ${GEMINI_API_KEY}
      
  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-1.5-pro
      api_key: ${GEMINI_API_KEY}
      
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: ${OPENAI_API_KEY}
      
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
      
  - model_name: claude-3-sonnet
    litellm_params:
      model: anthropic/claude-3-sonnet-20240229
      api_key: ${ANTHROPIC_API_KEY}

litellm_settings:
  drop_params: true
  set_verbose: false
```

3. **Update docker-compose.local.yml:**

```yaml
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: local-litellm
    ports:
      - "4000:4000"
    volumes:
      - ./litellm-config.yaml:/app/config.yaml
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    command: [
      "--config", "/app/config.yaml",
      "--port", "4000"
    ]
    networks:
      - local-ai-net
```

4. **Restart LiteLLM:**
   ```bash
   docker-compose -f docker-compose.local.yml up -d litellm
   ```

5. **In OpenWebUI, all models appear under one connection!**
