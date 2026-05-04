---
name: github-workflow-best-practices
description: 'Sub-skill of github-workflow: Best Practices.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


### 1. Workflow Organization

- Use reusable workflows for common operations
- Implement proper caching strategies
- Set appropriate timeouts for each job
- Use workflow dependencies wisely

### 2. Security

- Store secrets in GitHub Secrets
- Use OIDC for cloud authentication
- Implement least-privilege principles
- Audit workflow permissions regularly

### 3. Performance

- Cache dependencies between runs
- Use appropriate runner sizes
- Implement early termination for failures
- Optimize parallel execution

### 4. Cost Management

- Use self-hosted runners for heavy workloads
- Implement concurrency controls
- Cache Docker layers
- Skip redundant workflow runs
