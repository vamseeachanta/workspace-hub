---
name: github-actions-1-security-best-practices
description: 'Sub-skill of github-actions: 1. Security Best Practices (+3).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Security Best Practices (+3)

## 1. Security Best Practices

```yaml
# Always pin action versions with SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

# Use minimum required permissions
permissions:
  contents: read
  packages: write

# Never hardcode secrets
env:
  API_KEY: ${{ secrets.API_KEY }}  # Good
  # API_KEY: "sk-1234567890"       # Never do this

# Use OIDC for cloud provider authentication
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
```


## 2. Performance Optimization

```yaml
# Use caching aggressively
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ hashFiles('requirements.txt') }}

# Use matrix fail-fast wisely
strategy:
  fail-fast: false  # Continue other jobs on failure

# Limit concurrent runs
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```


## 3. Maintainability

```yaml
# Use reusable workflows
jobs:
  test:
    uses: ./.github/workflows/reusable-test.yml

# Extract common steps into composite actions
- uses: ./.github/actions/setup-project

# Use environment variables for configuration
env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '20'
```


## 4. Error Handling

```yaml
# Use continue-on-error for non-critical steps
- name: Optional step
  continue-on-error: true
  run: optional-command

# Add timeout to prevent stuck jobs
jobs:
  build:
    timeout-minutes: 30

# Always clean up resources
- name: Cleanup
  if: always()
  run: cleanup-command
```
