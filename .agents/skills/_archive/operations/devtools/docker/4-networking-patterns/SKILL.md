---
name: docker-4-networking-patterns
description: 'Sub-skill of docker: 4. Networking Patterns (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 4. Networking Patterns (+1)

## 4. Networking Patterns


**Custom Network Configuration:**
```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    networks:
      - frontend-network

  backend:
    build: ./backend
    networks:
      - frontend-network
      - backend-network

  db:
    image: postgres:16-alpine
    networks:
      - backend-network

networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge
    internal: true  # No external access
```

**Network Commands:**
```bash
# List networks
docker network ls

# Inspect network
docker network inspect app-network

# Create custom network
docker network create --driver bridge my-network

# Connect container to network
docker network connect my-network container-name

# Disconnect container
docker network disconnect my-network container-name
```


## 5. Volume Management


**Volume Types and Usage:**
```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    volumes:
      # Named volume (managed by Docker)
      - app_data:/app/data

      # Bind mount (host directory)
      - ./config:/app/config:ro

      # Anonymous volume (for excluding from bind mount)
      - /app/node_modules

      # tmpfs mount (in-memory)
      - type: tmpfs
        target: /app/tmp
        tmpfs:
          size: 100M

volumes:
  app_data:
    driver: local
    driver_opts:
      type: none
      device: /data/app
      o: bind
```

**Volume Commands:**
```bash
# List volumes
docker volume ls

# Create volume
docker volume create my-volume

# Inspect volume
docker volume inspect my-volume

# Remove unused volumes
docker volume prune

# Backup volume
docker run --rm -v my-volume:/data -v $(pwd):/backup alpine \
    tar czf /backup/volume-backup.tar.gz -C /data .

# Restore volume
docker run --rm -v my-volume:/data -v $(pwd):/backup alpine \
    tar xzf /backup/volume-backup.tar.gz -C /data
```
