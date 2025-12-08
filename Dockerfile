# ============================================================================
# STAGE 1: Builder
# ============================================================================
# Multi-stage builds reduce final image size
# We install dependencies here and copy to final stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
# These are only needed during build, not in final image
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
# If requirements don't change, Docker reuses this layer
COPY requirements.txt .

# Install to user directory (will copy to final stage)
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# STAGE 2: Final Runtime Image
# ============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
# This avoids having build tools in final image
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY agent/ ./agent/

# Create non-root user for security
# Never run containers as root!
RUN useradd -m -u 1000 agent && \
    chown -R agent:agent /app

# Switch to non-root user
USER agent

# Make scripts in .local available
ENV PATH=/root/.local/bin:$PATH

# Health check - Docker/K8s uses this to know if container is healthy
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# CMD vs ENTRYPOINT
# CMD can be overridden, ENTRYPOINT cannot
# We use CMD for flexibility
CMD ["python", "-m", "uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
