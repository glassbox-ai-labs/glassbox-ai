# GlassBox AI - Docker Image for GHCR deployment

FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py orchestrator.py trust_db.py ./

# Environment variables will be passed at runtime
ENV PYTHONUNBUFFERED=1

# Run MCP server
CMD ["python", "server.py"]
