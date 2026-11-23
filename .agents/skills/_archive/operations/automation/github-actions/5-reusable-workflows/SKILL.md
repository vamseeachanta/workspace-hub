---
name: github-actions-5-reusable-workflows
description: 'Sub-skill of github-actions: 5. Reusable Workflows (+5).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 5. Reusable Workflows (+5)

## 5. Reusable Workflows


```yaml
# .github/workflows/reusable-python-ci.yml
name: Reusable Python CI

on:
  workflow_call:
    inputs:
      python-version:
        description: 'Python version to use'
        required: false

*See sub-skills for full details.*

## 6. Composite Actions


```yaml
# .github/actions/setup-project/action.yml
name: 'Setup Project'
description: 'Set up Python environment with dependencies and caching'

inputs:
  python-version:
    description: 'Python version'
    required: false
    default: '3.11'

*See sub-skills for full details.*

## 7. Secrets and Environment Management


```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:

*See sub-skills for full details.*

## 8. Container Builds and Registry Publishing


```yaml
# .github/workflows/docker.yml
name: Docker Build and Push

on:
  push:
    branches: [main]
    tags: ['v*']
  pull_request:
    branches: [main]

*See sub-skills for full details.*

## 9. Scheduled Workflows and Maintenance


```yaml
# .github/workflows/maintenance.yml
name: Repository Maintenance

on:
  schedule:
    # Run every Monday at 6 AM UTC
    - cron: '0 6 * * 1'
  workflow_dispatch:


*See sub-skills for full details.*

## 10. PR Automation and Checks


```yaml
# .github/workflows/pr-checks.yml
name: PR Checks

on:
  pull_request:
    types: [opened, synchronize, reopened, edited]

permissions:
  contents: read

*See sub-skills for full details.*
