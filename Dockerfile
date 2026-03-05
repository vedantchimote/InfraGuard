# InfraGuard AIOps Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .
COPY scripts/ ./scripts/

# Create directories for runtime data
RUN mkdir -p /app/logs /app/models /app/config

# Create non-root user for security
RUN useradd -m -u 1000 infraguard && \
    chown -R infraguard:infraguard /app

# Switch to non-root user
USER infraguard

# Expose health check port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PROMETHEUS_URL=http://prometheus:9090 \
    LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "main.py", "--config", "/app/config/settings.yaml"]
