---
name: github-swarm-pr-2-status-checks
description: 'Sub-skill of github-swarm-pr: 2. Status Checks (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 2. Status Checks (+1)

## 2. Status Checks


```yaml
# Require swarm completion before merge
required_status_checks:
  contexts:
    - "swarm/review-complete"
    - "swarm/tests-validated"
    - "swarm/security-approved"
```

## 3. Review Quality


- Run security scan on all PRs touching auth code
- Require architect review for structural changes
- Auto-assign reviewers based on CODEOWNERS
- Use swarm consensus for merge decisions
