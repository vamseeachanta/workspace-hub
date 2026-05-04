---
name: windmill-1-script-organization
description: 'Sub-skill of windmill: 1. Script Organization (+3).'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 1. Script Organization (+3)

## 1. Script Organization

```
scripts/
├── data/
│   ├── fetch_api_data.py
│   ├── transform_records.ts
│   └── aggregate_metrics.py
├── integrations/
│   ├── sync_crm.py
│   ├── webhook_handler.ts
│   └── slack_notifications.py
├── devops/
│   ├── deploy_service.sh
│   ├── health_checks.py
│   └── cleanup_resources.py
└── admin/
    ├── manage_resources.py
    └── user_management.py
```


## 2. Error Handling

```python
import wmill

def main(input_data: dict):
    try:
        result = process_data(input_data)
        return {"success": True, "data": result}
    except ValueError as e:
        # Business logic error - don't retry
        wmill.set_state({"error": str(e), "retryable": False})
        raise
    except ConnectionError as e:
        # Transient error - allow retry
        wmill.set_state({"error": str(e), "retryable": True})
        raise
```


## 3. Resource Management

```python
# Always use resources for credentials
api_key = wmill.get_resource("u/admin/api_key")  # Good
# api_key = "sk-1234567890"  # Never hardcode

# Use variables for configuration
config = wmill.get_variable("u/admin/app_config")
```


## 4. Testing Scripts

```bash
# Test script locally
wmill script run f/data/fetch_api_data \
  --data '{"api_endpoint": "https://api.example.com", "limit": 10}'

# Run with specific resource
wmill script run f/data/fetch_api_data \
  --resource u/admin/test_api_credentials
```
