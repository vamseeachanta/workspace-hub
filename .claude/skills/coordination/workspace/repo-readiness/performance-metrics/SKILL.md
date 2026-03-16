---
name: repo-readiness-performance-metrics
description: 'Sub-skill of repo-readiness: Performance Metrics (+2).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Performance Metrics (+2)

## Performance Metrics


| Metric | Target | Measurement |
|--------|--------|-------------|
| Check Time | < 5 seconds | Time to complete all checks |
| Accuracy | > 95% | Correct readiness assessment |
| False Positives | < 5% | Incorrectly marked as ready |
| False Negatives | < 2% | Incorrectly marked as not ready |
| Cache Hit Rate | > 80% | Using cached readiness data |

## Coverage Metrics


| Metric | Target | Current |
|--------|--------|---------|
| Repos with CLAUDE.md | 100% | Track per repo |
| Repos with mission.md | 100% | Track per repo |
| Structure compliance | > 95% | Average across repos |
| Standards adherence | > 90% | Average compliance score |

## Adoption Metrics


| Metric | Target | Measurement |
|--------|--------|-------------|
| Hook installation | 100% repos | Pre-task hook installed |
| Auto-execution rate | > 95% | Tasks with readiness check |
| Manual check usage | > 10/week | Explicit readiness checks |
| Issue detection | > 50% | Issues caught before work |
