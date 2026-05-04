---
name: teams-api-common-issues
description: 'Sub-skill of teams-api: Common Issues.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: Bot not receiving messages**
```bash
# Verify messaging endpoint is accessible
curl -X POST https://your-bot.azurewebsites.net/api/messages \
  -H "Content-Type: application/json" \
  -d '{"type": "ping"}'

# Check Azure App Registration permissions
# Verify Teams channel is enabled in Bot Framework
```

**Issue: Webhook returns error**
```python
# Debug webhook response
response = requests.post(webhook_url, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
```

**Issue: Graph API permission denied**
```bash
# Verify API permissions are granted
# Admin consent may be required for application permissions
# Check token scopes match required permissions
```
