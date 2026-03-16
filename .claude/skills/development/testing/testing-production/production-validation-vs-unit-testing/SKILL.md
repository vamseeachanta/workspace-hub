---
name: testing-production-production-validation-vs-unit-testing
description: 'Sub-skill of testing-production: Production Validation vs Unit Testing
  (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Production Validation vs Unit Testing (+1)

## Production Validation vs Unit Testing


| Aspect | Unit Tests (TDD) | Production Validation |
|--------|------------------|----------------------|
| Dependencies | Mocked | Real |
| Database | In-memory/fake | Actual PostgreSQL/etc |
| APIs | Stubbed responses | Live service calls |
| Purpose | Design/logic | Deployment readiness |
| Speed | Fast (ms) | Slower (seconds) |

## Validation Categories


1. **Implementation Completeness**: No mock/stub/fake code in production
2. **Database Integration**: CRUD operations on real database
3. **External APIs**: Actual service integrations work
4. **Infrastructure**: Cache, email, queues function correctly
5. **Performance**: Meets latency and throughput requirements
6. **Security**: Authentication, authorization, input validation
