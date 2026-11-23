---
name: github-actions-common-issues
description: 'Sub-skill of github-actions: Common Issues (+1).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: Workflow not triggering**
```yaml
# Check trigger paths
on:
  push:
    paths:
      - 'src/**'  # Only triggers for src/ changes

# Verify branch names match
on:
  push:
    branches:
      - main
      - 'release/*'  # Use quotes for patterns
```

**Issue: Cache not restoring**
```yaml
# Verify cache key matches
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ runner.os }}-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      pip-${{ runner.os }}-
```

**Issue: Secrets not available**
```yaml
# Secrets not available in forks
- name: Deploy
  if: github.event.pull_request.head.repo.full_name == github.repository
  env:
    SECRET: ${{ secrets.MY_SECRET }}
```

**Issue: Permission denied**
```yaml
# Add required permissions
permissions:
  contents: write
  packages: write
  pull-requests: write
```


## Debugging Workflows


```yaml
# Enable debug logging
jobs:
  debug:
    runs-on: ubuntu-latest
    steps:
      - name: Dump context
        env:
          GITHUB_CONTEXT: ${{ toJson(github) }}
          JOB_CONTEXT: ${{ toJson(job) }}
          STEPS_CONTEXT: ${{ toJson(steps) }}
        run: |
          echo "GitHub context:"
          echo "$GITHUB_CONTEXT"
          echo "Job context:"
          echo "$JOB_CONTEXT"
```
