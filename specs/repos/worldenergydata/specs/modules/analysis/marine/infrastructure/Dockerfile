# Marine Safety Incidents Database - Multi-stage Docker Build
# Purpose: Production-ready containerized Python API
# Build: docker build -t marine-safety-api:latest .
# Run: docker run -p 8000:8000 --env-file .env marine-safety-api:latest

# ============================================================================
# Stage 1: Builder - Install dependencies and compile Python packages
# ============================================================================
FROM python:3.11-slim-bookworm AS builder

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies in virtual environment
# Use --no-deps to avoid installing sub-dependencies twice
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    pip install gunicorn uvicorn[standard]

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim-bookworm AS runtime

# Set metadata labels
LABEL maintainer="data-team@example.com" \
      description="Marine Safety Incidents Database API" \
      version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    PORT=8000

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -s /sbin/nologin appuser

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . /app/

# Create directories for data and logs
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose application port
EXPOSE ${PORT}

# Default command: Run with Gunicorn and Uvicorn workers
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "app.main:app"]

# ============================================================================
# Alternative Stage: Development - Include dev tools and debugging
# ============================================================================
FROM runtime AS development

# Switch back to root to install dev tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    less \
    git \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy dev requirements and install
COPY requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

# Install code quality tools
RUN pip install \
    black \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    pytest-asyncio \
    ipython \
    ipdb

# Switch back to appuser
USER appuser

# Development command: Run with auto-reload
CMD ["uvicorn", \
     "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload", \
     "--log-level", "debug"]

# ============================================================================
# Build Instructions:
# ============================================================================
#
# Production build:
#   docker build --target runtime -t marine-safety-api:latest .
#
# Development build:
#   docker build --target development -t marine-safety-api:dev .
#
# Build with specific version tag:
#   docker build -t marine-safety-api:v1.0.0 .
#
# Multi-platform build (for AWS ARM instances):
#   docker buildx build --platform linux/amd64,linux/arm64 -t marine-safety-api:latest .
#
# Push to ECR:
#   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
#   docker tag marine-safety-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/marine-safety-api:latest
#   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/marine-safety-api:latest
#
# ============================================================================
