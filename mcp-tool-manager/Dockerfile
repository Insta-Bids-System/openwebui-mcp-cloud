# Production Dockerfile for MCP Tool Manager
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mcp_tool_manager.py .
COPY desktop_commander_wrapper.py .
COPY github_wrapper.py .
COPY cache_manager.py .
COPY monitoring_dashboard.py .
COPY auto_scaler.py .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9090/health || exit 1

# Expose ports
EXPOSE 8000 9090

# Run the application
CMD ["python", "-m", "uvicorn", "mcp_tool_manager:app", "--host", "0.0.0.0", "--port", "8000"]
