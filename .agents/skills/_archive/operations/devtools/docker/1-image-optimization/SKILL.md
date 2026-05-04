---
name: docker-1-image-optimization
description: 'Sub-skill of docker: 1. Image Optimization (+4).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Image Optimization (+4)

## 1. Image Optimization


```dockerfile
# Use specific versions
FROM python:3.12.1-slim  # Not :latest

# Combine RUN commands to reduce layers
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Use .dockerignore
# .dockerignore
.git
.gitignore
node_modules
npm-debug.log
Dockerfile*
docker-compose*
.dockerignore
.env*
*.md
.pytest_cache
__pycache__
*.pyc
.coverage
htmlcov
```


## 2. Security Best Practices


```dockerfile
# Run as non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# Don't store secrets in images
# Use environment variables or secrets management

# Scan images for vulnerabilities
# docker scan myimage:latest

# Use read-only filesystem where possible
# docker run --read-only myimage
```


## 3. Layer Caching Strategy


```dockerfile
# Order from least to most frequently changed
FROM node:20-alpine

# 1. System dependencies (rarely change)
RUN apk add --no-cache git

# 2. Package manifests (change sometimes)
COPY package*.json ./
RUN npm ci

# 3. Application code (changes often)
COPY . .

# 4. Build step
RUN npm run build
```


## 4. Health Checks


```dockerfile
# HTTP health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# TCP health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD nc -z localhost 5432 || exit 1

# Custom script
HEALTHCHECK --interval=30s --timeout=10s \
    CMD /app/healthcheck.sh || exit 1
```


## 5. Logging Best Practices


```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service,environment"
        env: "NODE_ENV"
```
