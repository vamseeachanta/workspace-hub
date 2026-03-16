---
name: github-release-swarm-progressive-deployment
description: 'Sub-skill of github-release-swarm: Progressive Deployment.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Progressive Deployment

## Progressive Deployment


```yaml
# Staged rollout configuration
deployment:
  strategy: progressive
  stages:
    - name: canary
      percentage: 5
      duration: 1h
      metrics:
        - error-rate < 0.1%
        - latency-p99 < 200ms

    - name: partial
      percentage: 25
      duration: 4h
      validation: automated-tests

    - name: full
      percentage: 100
      approval: required
```
