---
name: testing-production-execution-checklist
description: 'Sub-skill of testing-production: Execution Checklist.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


- [ ] Scan for mock/fake/stub implementations
- [ ] Scan for TODO/FIXME comments
- [ ] Verify all environment variables configured
- [ ] Test database CRUD with real database
- [ ] Test external APIs with real (test mode) services
- [ ] Test infrastructure (cache, email, queues)
- [ ] Validate performance under load
- [ ] Verify security measures (auth, input validation)
- [ ] Test health check endpoint
- [ ] Verify graceful shutdown handling
