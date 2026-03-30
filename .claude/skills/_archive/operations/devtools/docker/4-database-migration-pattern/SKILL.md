---
name: docker-4-database-migration-pattern
description: 'Sub-skill of docker: 4. Database Migration Pattern.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 4. Database Migration Pattern

## 4. Database Migration Pattern


**Migration Service:**
```yaml
# docker-compose.yml
services:
  migrate:
    build:
      context: .
      dockerfile: Dockerfile
    command: npm run migrate
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      db:
        condition: service_healthy
    profiles:
      - migrate  # Only run when explicitly requested

  seed:
    build:
      context: .
      dockerfile: Dockerfile
    command: npm run seed
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
    depends_on:
      - migrate
    profiles:
      - seed
```

**Usage:**
```bash
# Run migrations
docker compose --profile migrate up migrate

# Run migrations and seed
docker compose --profile migrate --profile seed up
```
