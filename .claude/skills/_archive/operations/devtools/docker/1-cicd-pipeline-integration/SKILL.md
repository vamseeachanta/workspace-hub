---
name: docker-1-cicd-pipeline-integration
description: 'Sub-skill of docker: 1. CI/CD Pipeline Integration (+2).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. CI/CD Pipeline Integration (+2)

## 1. CI/CD Pipeline Integration


**GitHub Actions Workflow:**
```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint Dockerfile
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile

  build:
    runs-on: ubuntu-latest
    needs: lint
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix=
            type=raw,value=latest,enable=${{ github.ref == 'refs/heads/main' }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
```


## 2. Local Development with Hot Reload


**Development Dockerfile:**
```dockerfile
# Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

# Install development dependencies
RUN apk add --no-cache git

# Install nodemon globally for hot reload
RUN npm install -g nodemon

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies)
RUN npm install

# Don't copy source - use volume mount instead
# Source will be mounted at runtime

EXPOSE 3000

# Use nodemon for hot reload
CMD ["nodemon", "--watch", "src", "--ext", "js,ts,json", "src/index.js"]
```

**Development Compose:**
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - ./src:/app/src
      - ./package.json:/app/package.json
    ports:
      - "3000:3000"
      - "9229:9229"  # Debug port
    environment:
      - NODE_ENV=development
      - DEBUG=app:*
    command: nodemon --inspect=0.0.0.0:9229 src/index.js
```


## 3. Multi-Environment Configuration


**Environment-Specific Compose Files:**
```bash
# Directory structure
docker/
├── docker-compose.yml          # Base configuration
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.test.yml     # Test environment
├── docker-compose.prod.yml     # Production configuration
└── .env.example                # Environment template
```

**Usage:**
```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Testing
docker compose -f docker-compose.yml -f docker-compose.test.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
