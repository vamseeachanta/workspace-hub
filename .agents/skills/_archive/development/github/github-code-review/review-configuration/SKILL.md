---
name: github-code-review-review-configuration
description: 'Sub-skill of github-code-review: Review Configuration.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Review Configuration

## Review Configuration


```yaml
# .github/review-swarm.yml
version: 1
review:
  auto-trigger: true
  required-agents:
    - security
    - performance
    - style
  optional-agents:
    - architecture
    - accessibility
    - i18n

  thresholds:
    security: block
    performance: warn
    style: suggest

  rules:
    security:
      - no-eval
      - no-hardcoded-secrets
      - proper-auth-checks
    performance:

*See sub-skills for full details.*
