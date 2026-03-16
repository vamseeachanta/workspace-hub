---
name: time-tracking-common-issues
description: 'Sub-skill of time-tracking: Common Issues.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Common Issues

## Common Issues


**Issue: 403 Forbidden (Toggl)**
```python
# Check API token
curl -u "YOUR_TOKEN:api_token" "https://api.track.toggl.com/api/v9/me"

# Ensure token has proper permissions
# Regenerate token at: https://track.toggl.com/profile
```

**Issue: Empty response (RescueTime)**
```python
# Check if data exists for date range
# RescueTime only has data when the client is running

# Verify API key
curl "https://www.rescuetime.com/anapi/data?key=YOUR_KEY&format=json"
```

**Issue: Time zone issues**
```python
# Always use UTC for Toggl API
from datetime import datetime, timezone

start = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
```

**Issue: Duration calculation**
```python
# Running entries have negative duration
entry = toggl.get_current_entry()
if entry and entry.get("duration", 0) < 0:
    # Calculate actual duration
    start = datetime.fromisoformat(entry["start"].replace("Z", "+00:00"))
    duration = (datetime.now(timezone.utc) - start).total_seconds()
```
