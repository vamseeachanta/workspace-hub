---
name: background-service-manager-metrics
description: 'Sub-skill of background-service-manager: Metrics.'
version: 2.0.0
category: operations
type: reference
scripts_exempt: true
---

# Metrics

## Metrics


| Metric | Target | How to Measure |
|--------|--------|----------------|
| Uptime | >99.9% | Time running / total time |
| Restart count | <1/day | Number of restarts needed |
| Memory usage | <80% limit | ps output / allocated |
| CPU usage | <70% average | ps output over time |
| Log size | <100MB/day | Log file growth rate |
| Graceful shutdowns | 100% | Clean stops / total stops |
