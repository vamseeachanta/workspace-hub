---
name: automation-best-practices
description: 'Sub-skill of automation: Best Practices.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


### 1. Version Control Workflows

```bash
# Store workflow definitions in git
git add automation/workflows/
git commit -m "feat: Add data sync workflow"
```

### 2. Environment Separation

```yaml
# Use environment-specific configurations
production:
  schedule: "0 */6 * * *"
  parallelism: 10
development:
  schedule: null  # Manual trigger only
  parallelism: 2
```

### 3. Monitoring and Alerting

```python
# Add observability to all workflows
def with_monitoring(workflow_name):
    start_time = time.time()
    try:
        result = execute_workflow()
        metrics.record_success(workflow_name, time.time() - start_time)
        return result
    except Exception as e:
        metrics.record_failure(workflow_name, str(e))
        alerts.send(f"Workflow {workflow_name} failed: {e}")
        raise
```

### 4. Documentation

```yaml
# Document workflow purpose and dependencies
# ABOUTME: Syncs customer data from CRM to data warehouse
# ABOUTME: Depends on: crm-api, warehouse-connection
# ABOUTME: Schedule: Every 6 hours
```
