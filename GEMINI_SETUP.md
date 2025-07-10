# 🤖 Gemini API Configuration for OpenWebUI

## Option 1: Using LiteLLM Proxy (Recommended)

### Step 1: Add LiteLLM to Docker Compose

Add this service to your `docker-compose.yml`:

```yaml
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: litellm
    restart: unless-stopped
    ports:
      - "4000:4000"
    environment:
      - GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
    command: |
      --model gemini/gemini-pro
      --model gemini/gemini-pro-vision
      --port 4000
    networks:
      - dev-net
```

### Step 2: Restart Docker Compose

```bash
docker-compose down
docker-compose up -d
```

### Step 3: Configure in OpenWebUI

1. Go to Settings → Connections
2. Click "OpenAI-Compatible"
3. Configure:
   - **API Base URL**: `http://localhost:4000/v1`
   - **API Key**: `any-string-here` (LiteLLM doesn't check)
4. Click "Save"

## Option 2: Direct Configuration (if supported)

### Check if Google AI is Available

1. Go to Settings → Connections
2. Look for "Google AI" or "Gemini"
3. If available:
   - Enter API Key: `YOUR_GEMINI_API_KEY_HERE`
   - Save

## Option 3: Using Environment Variable

Add to your `.env` file:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

Then check Settings → Connections for Google AI option.

## Available Gemini Models

Once configured, you'll have access to:
- `gemini-pro` - Text generation
- `gemini-pro-vision` - Multimodal (text + images)
- `gemini-1.5-pro` - Latest model (if available)

## Testing

After configuration:
1. Go to main chat
2. Select a Gemini model from dropdown
3. Test with: "Hello, are you Gemini?"

## Troubleshooting

### If models don't appear:
1. Check LiteLLM logs: `docker logs litellm`
2. Verify API key is valid
3. Try restarting OpenWebUI: `docker-compose restart open-webui-dev`

### API Key Limits:
- Free tier: 60 requests per minute
- Check usage: https://makersuite.google.com/app/apikey