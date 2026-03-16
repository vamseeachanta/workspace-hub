---
name: docker
version: 1.0.0
description: Complete Docker containerization patterns with multi-stage builds for
  development and production workflows
author: workspace-hub
category: operations
capabilities:
- Dockerfile best practices and multi-stage builds
- Docker Compose orchestration and networking
- Volume management and data persistence
- Development vs production configurations
- Container debugging and optimization
- Registry management and image distribution
tools:
- docker
- docker-compose
- buildx
- dive
- hadolint
tags:
- docker
- containers
- devops
- orchestration
- microservices
- compose
platforms:
- linux
- macos
- windows
related_skills:
- cli-productivity
- git-advanced
requires: []
see_also:
- docker-1-basic-dockerfile-patterns
- docker-2-multi-stage-builds
- docker-3-docker-compose-for-development
- docker-4-networking-patterns
- docker-6-development-workflow-scripts
- docker-1-cicd-pipeline-integration
- docker-4-database-migration-pattern
- docker-1-image-optimization
- docker-common-issues-and-solutions
scripts_exempt: true
---

# Docker

## When to Use This Skill

### USE when:

- Building reproducible development environments
- Creating consistent CI/CD pipelines
- Deploying microservices architectures
- Isolating application dependencies
- Packaging applications for distribution
- Setting up local development with multiple services
- Need portable environments across teams
### DON'T USE when:

- Simple scripts that don't need isolation
- Applications that require direct hardware access
- Environments where containers aren't permitted
- Tasks better suited for virtual machines (full OS isolation)
- When simpler alternatives like venv suffice

## Prerequisites

### Installation

**Linux (Ubuntu/Debian):**
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker


*See sub-skills for full details.*

## Version History

- **1.0.0** (2026-01-17): Initial release
  - Dockerfile best practices and multi-stage builds
  - Docker Compose orchestration patterns
  - Development and production configurations
  - CI/CD integration examples
  - Networking and volume management
  - Troubleshooting guide

---

**Use this skill to build consistent, reproducible containerized environments across development, testing, and production!**

## Sub-Skills

- [1. Basic Dockerfile Patterns](1-basic-dockerfile-patterns/SKILL.md)
- [2. Multi-Stage Builds](2-multi-stage-builds/SKILL.md)
- [3. Docker Compose for Development](3-docker-compose-for-development/SKILL.md)
- [4. Networking Patterns (+1)](4-networking-patterns/SKILL.md)
- [6. Development Workflow Scripts](6-development-workflow-scripts/SKILL.md)
- [1. CI/CD Pipeline Integration (+2)](1-cicd-pipeline-integration/SKILL.md)
- [4. Database Migration Pattern](4-database-migration-pattern/SKILL.md)
- [1. Image Optimization (+4)](1-image-optimization/SKILL.md)
- [Common Issues and Solutions (+1)](common-issues-and-solutions/SKILL.md)
