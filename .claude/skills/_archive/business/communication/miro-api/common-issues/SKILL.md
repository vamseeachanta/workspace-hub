---
name: miro-api-common-issues
description: 'Sub-skill of miro-api: Common Issues (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues (+1)

## Common Issues


**Issue: 401 Unauthorized**
```python
# Verify token is valid
import requests

def verify_token(token: str) -> bool:
    response = requests.get(
        "https://api.miro.com/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.status_code == 200

# Check token scopes
def get_token_scopes(token: str) -> list:
    response = requests.get(
        "https://api.miro.com/v1/oauth-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json().get("scopes", [])
```

**Issue: Items not appearing on board**
```python
# Check board permissions
def check_board_access(board_id: str) -> dict:
    board = miro.boards.get(board_id)
    return {
        "id": board.id,
        "permissions": board.policy.permissions_policy,
        "sharing": board.policy.sharing_policy,
    }
```

**Issue: Rate limiting**
```python
# Implement exponential backoff
import time

def with_backoff(func, max_retries=5):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e):
                wait = (2 ** i) + (random.random() * 0.1)
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")
```


## Debug Commands


```bash
# Test API authentication
curl -X GET "https://api.miro.com/v1/users/me" \
  -H "Authorization: Bearer $MIRO_ACCESS_TOKEN"

# List boards
curl -X GET "https://api.miro.com/v2/boards?team_id=$MIRO_TEAM_ID" \
  -H "Authorization: Bearer $MIRO_ACCESS_TOKEN"

# Get board details
curl -X GET "https://api.miro.com/v2/boards/$BOARD_ID" \
  -H "Authorization: Bearer $MIRO_ACCESS_TOKEN"

# Create sticky note
curl -X POST "https://api.miro.com/v2/boards/$BOARD_ID/sticky_notes" \
  -H "Authorization: Bearer $MIRO_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"content": "Test note"}, "position": {"x": 0, "y": 0}}'
```
