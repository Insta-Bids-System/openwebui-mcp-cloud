FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    mcp \
    fastmcp \
    aiohttp \
    redis \
    asyncio \
    urllib3 \
    fastapi \
    uvicorn \
    pydantic \
    httpx

# Copy application code
COPY . /app

# Create workspace directory
RUN mkdir -p /workspace

# Expose port for HTTP server
EXPOSE 8888

# Run the HTTP server
CMD ["python", "-m", "http_server"]
