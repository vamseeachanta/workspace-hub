---
name: docker-6-development-workflow-scripts
description: 'Sub-skill of docker: 6. Development Workflow Scripts.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 6. Development Workflow Scripts

## 6. Development Workflow Scripts


**Makefile for Docker Operations:**
```makefile
# Makefile
.PHONY: build up down logs shell test clean

# Variables
COMPOSE := docker compose
PROJECT := myapp

# Build images
build:
	$(COMPOSE) build --no-cache

# Start services
up:
	$(COMPOSE) up -d

# Start with logs
up-logs:
	$(COMPOSE) up

# Stop services
down:
	$(COMPOSE) down

# Stop and remove volumes
down-clean:
	$(COMPOSE) down -v --remove-orphans

# View logs
logs:
	$(COMPOSE) logs -f

# Logs for specific service
logs-%:
	$(COMPOSE) logs -f $*

# Shell into app container
shell:
	$(COMPOSE) exec app sh

# Run tests
test:
	$(COMPOSE) exec app npm test

# Lint Dockerfiles
lint:
	hadolint Dockerfile
	hadolint Dockerfile.prod

# Analyze image
analyze:
	dive $(PROJECT):latest

# Clean up
clean:
	docker system prune -f
	docker volume prune -f

# Production build and push
prod-build:
	docker build -t $(PROJECT):latest -f Dockerfile.prod .

prod-push:
	docker push $(PROJECT):latest
```

**Development Helper Script:**
```bash
#!/bin/bash
# scripts/docker-dev.sh
# ABOUTME: Docker development helper script
# ABOUTME: Provides common Docker operations for development

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Commands
case "$1" in
    start)
        log_info "Starting development environment..."
        docker compose up -d
        log_info "Services started. Run 'docker compose logs -f' to view logs."
        ;;
    stop)
        log_info "Stopping development environment..."
        docker compose down
        ;;
    restart)
        log_info "Restarting services..."
        docker compose restart
        ;;
    rebuild)
        log_info "Rebuilding images..."
        docker compose build --no-cache
        docker compose up -d
        ;;
    logs)
        docker compose logs -f "${2:-}"
        ;;
    shell)
        SERVICE="${2:-app}"
        log_info "Opening shell in $SERVICE..."
        docker compose exec "$SERVICE" sh
        ;;
    db)
        log_info "Connecting to database..."
        docker compose exec db psql -U devuser -d devdb
        ;;
    reset-db)
        log_warn "This will delete all data. Continue? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            docker compose down -v
            docker compose up -d db
            log_info "Database reset complete."
        fi
        ;;
    clean)
        log_warn "Cleaning up Docker resources..."
        docker compose down -v --remove-orphans
        docker system prune -f
        ;;
    status)
        docker compose ps
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|rebuild|logs|shell|db|reset-db|clean|status}"
        echo ""
        echo "Commands:"
        echo "  start     - Start all services"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  rebuild   - Rebuild images and restart"
        echo "  logs      - View logs (optional: service name)"
        echo "  shell     - Open shell in container (default: app)"
        echo "  db        - Connect to database"
        echo "  reset-db  - Reset database (deletes all data)"
        echo "  clean     - Clean up all Docker resources"
        echo "  status    - Show service status"
        exit 1
        ;;
esac
```
