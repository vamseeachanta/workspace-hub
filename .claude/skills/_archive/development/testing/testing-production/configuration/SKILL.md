---
name: testing-production-configuration
description: 'Sub-skill of testing-production: Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


```yaml
production_validation:
  scan:
    patterns:
      - "mock"
      - "fake"
      - "stub"
      - "TODO"
      - "FIXME"
      - "not implemented"
    exclude_dirs:
      - "__tests__"
      - "tests"
      - "spec"
      - "node_modules"
    exclude_files:
      - "*.test.*"
      - "*.spec.*"

  database:
    use_real: true
    host: ${TEST_DB_HOST}
    cleanup_after: true

  external_apis:
    use_test_mode: true
    timeout_ms: 30000
    retry_count: 3

  performance:
    concurrent_requests: 100
    max_latency_ms: 200
    min_throughput_rps: 1000
    sustained_duration_s: 60
```
