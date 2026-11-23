---
name: testing-tdd-london-configuration
description: 'Sub-skill of testing-tdd-london: Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Configuration

## Configuration


```yaml
london_tdd_config:
  testing:
    framework: jest
    mock_library: jest  # or sinon, testdouble
    strict_mocks: true  # fail on unexpected calls

  coverage:
    interaction_coverage: true
    verify_all_mocks: true

  swarm_coordination:
    share_contracts: true
    sync_mock_definitions: true

  patterns:
    verify_call_order: true
    verify_call_count: true
    verify_call_args: true
```
