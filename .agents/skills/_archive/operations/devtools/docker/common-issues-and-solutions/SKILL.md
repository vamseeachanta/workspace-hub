---
name: docker-common-issues-and-solutions
description: 'Sub-skill of docker: Common Issues and Solutions (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues and Solutions (+1)

## Common Issues and Solutions


**Container won't start:**
```bash
# Check logs
docker logs container-name

# Check container status
docker inspect container-name

# Run interactively to debug
docker run -it --entrypoint sh image-name
```

**Permission denied errors:**
```bash
# Fix file ownership
docker run --rm -v $(pwd):/app alpine chown -R $(id -u):$(id -g) /app

# Or use user namespace remapping
```

**Out of disk space:**
```bash
# Clean up unused resources
docker system prune -a --volumes

# Check disk usage
docker system df
```

**Slow builds:**
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Use cache mounts
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
```

**Network connectivity issues:**
```bash
# Check network
docker network inspect bridge

# Test connectivity
docker exec container-name ping other-container

# Check DNS resolution
docker exec container-name nslookup service-name
```


## Debug Commands


```bash
# Shell into running container
docker exec -it container-name sh

# Copy files from container
docker cp container-name:/app/logs ./logs

# View container processes
docker top container-name

# Monitor resource usage
docker stats

# View container changes
docker diff container-name

# Export container filesystem
docker export container-name > container.tar
```
