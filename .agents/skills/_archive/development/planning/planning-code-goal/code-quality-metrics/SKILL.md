---
name: planning-code-goal-code-quality-metrics
description: 'Sub-skill of planning-code-goal: Code Quality Metrics (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Code Quality Metrics (+2)

## Code Quality Metrics


| Metric | Target | Measurement |
|--------|--------|-------------|
| Cyclomatic Complexity | < 10 | Per function |
| Code Duplication | < 3% | Codebase-wide |
| Test Coverage | > 80% | Line coverage |
| Technical Debt Ratio | < 5% | SonarQube |

## Performance Metrics


| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time (p99) | < 200ms | APM |
| Throughput | > 1000 req/s | Load test |
| Error Rate | < 0.1% | Monitoring |
| Availability | > 99.9% | Uptime |

## Delivery Metrics


| Metric | Target | Measurement |
|--------|--------|-------------|
| Lead Time | < 1 day | Deploy tracking |
| Deploy Frequency | > 1/day | CI/CD |
| MTTR | < 1 hour | Incident tracking |
| Change Failure Rate | < 5% | Rollback rate |
