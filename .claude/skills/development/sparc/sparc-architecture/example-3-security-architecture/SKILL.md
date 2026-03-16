---
name: sparc-architecture-example-3-security-architecture
description: 'Sub-skill of sparc-architecture: Example 3: Security Architecture (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 3: Security Architecture (+1)

## Example 3: Security Architecture


```yaml
security_architecture:
  authentication:
    methods:
      - jwt_tokens:
          algorithm: RS256
          expiry: 15m
          refresh_expiry: 7d

      - oauth2:
          providers: [google, github]
          scopes: [email, profile]

      - mfa:
          methods: [totp, sms]
          required_for: [admin_roles]

  authorization:
    model: RBAC
    implementation:
      - role_hierarchy: true
      - resource_permissions: true
      - attribute_based: false

    example_roles:
      admin:
        permissions: ["*"]

      user:
        permissions:
          - "users:read:self"
          - "users:update:self"
          - "posts:create"
          - "posts:read"

  encryption:
    at_rest:
      - database: "AES-256"
      - file_storage: "AES-256"

    in_transit:
      - api: "TLS 1.3"
      - internal: "mTLS"

  compliance:
    - GDPR:
        data_retention: "2 years"
        right_to_forget: true
        data_portability: true

    - SOC2:
        audit_logging: true
        access_controls: true
        encryption: true
```


## Example 4: Scalability Design


```yaml
scalability_patterns:
  horizontal_scaling:
    services:
      - auth_service: "2-10 instances"
      - user_service: "2-20 instances"
      - notification_service: "1-5 instances"

    triggers:
      - cpu_utilization: "> 70%"
      - memory_utilization: "> 80%"
      - request_rate: "> 1000 req/sec"
      - response_time: "> 200ms p95"

  caching_strategy:
    layers:
      - cdn: "CloudFlare"
      - api_gateway: "30s TTL"
      - application: "Redis"
      - database: "Query cache"

    cache_keys:
      - "user:{id}": "5 min TTL"
      - "permissions:{userId}": "15 min TTL"
      - "session:{token}": "Until expiry"

  database_scaling:
    read_replicas: 3
    connection_pooling:
      min: 10
      max: 100

    sharding:
      strategy: "hash(user_id)"
      shards: 4
```
