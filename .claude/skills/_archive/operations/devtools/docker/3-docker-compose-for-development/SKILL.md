---
name: docker-3-docker-compose-for-development
description: 'Sub-skill of docker: 3. Docker Compose for Development.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 3. Docker Compose for Development

## 3. Docker Compose for Development


**Full Stack Development Environment:**
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Application service
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: builder  # Use builder stage for development
    volumes:
      - .:/app
      - /app/node_modules  # Exclude node_modules from bind mount
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://devuser:devpass@db:5432/devdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev
    networks:
      - app-network

  # Database service
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      POSTGRES_DB: devdb
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devuser -d devdb"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Redis cache
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    networks:
      - app-network

  # Adminer for database management
  adminer:
    image: adminer:latest
    ports:
      - "8080:8080"
    depends_on:
      - db
    networks:
      - app-network

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - app
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
```

**Development Override File:**
```yaml
# docker-compose.override.yml (automatically applied)
version: '3.8'

services:
  app:
    build:
      target: builder
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
    command: npm run dev:watch

  db:
    ports:
      - "5432:5432"  # Expose for local tools

  redis:
    ports:
      - "6379:6379"  # Expose for local tools
```

**Production Compose File:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    restart: always
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  db:
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```
