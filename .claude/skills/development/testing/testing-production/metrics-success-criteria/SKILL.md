---
name: testing-production-metrics-success-criteria
description: 'Sub-skill of testing-production: Metrics & Success Criteria.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Metrics & Success Criteria

## Metrics & Success Criteria


| Validation | Pass Criteria |
|------------|---------------|
| Mock-Free Code | 0 mock/fake/stub in production code |
| Database Integration | All CRUD operations work |
| API Integration | All external APIs respond correctly |
| Performance | p99 < 200ms, > 1000 req/s |
| Security | All auth/authz tests pass |
| Health Check | Returns healthy status |
| Error Rate | < 0.1% under load |
