---
name: sparc-architecture-configuration
description: 'Sub-skill of sparc-architecture: Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


```yaml
# sparc-architecture-config.yaml
architecture_settings:
  style: "microservices"  # monolith, microservices, serverless
  diagram_format: "mermaid"

infrastructure:
  container_runtime: "docker"
  orchestration: "kubernetes"
  cloud_provider: "aws"

api_design:
  style: "rest"  # rest, graphql, grpc
  versioning: "url"  # url, header
  documentation: "openapi"

security:
  authentication: "jwt"
  authorization: "rbac"
  encryption_at_rest: "aes-256"
  encryption_in_transit: "tls-1.3"
```
