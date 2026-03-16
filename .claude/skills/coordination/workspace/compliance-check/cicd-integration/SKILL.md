---
name: compliance-check-cicd-integration
description: 'Sub-skill of compliance-check: CI/CD Integration (+1).'
version: 1.1.0
category: coordination
type: reference
scripts_exempt: true
---

# CI/CD Integration (+1)

## CI/CD Integration


```yaml
# .github/workflows/compliance.yml
name: Compliance Check

on: [push, pull_request]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:

*See sub-skills for full details.*

## Scheduled Compliance Scan


```yaml
# Run weekly compliance scan
name: Weekly Compliance Scan

on:
  schedule:
    - cron: '0 9 * * 1'  # Monday 9am

jobs:
  scan:

*See sub-skills for full details.*
