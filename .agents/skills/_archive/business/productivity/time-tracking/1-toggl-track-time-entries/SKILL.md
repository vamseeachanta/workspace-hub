---
name: time-tracking-1-toggl-track-time-entries
description: 'Sub-skill of time-tracking: 1. Toggl Track - Time Entries.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. Toggl Track - Time Entries

## 1. Toggl Track - Time Entries


**REST API - Time Entries:**
```bash
# Get current running time entry
curl -s -u "$TOGGL_API_TOKEN:api_token" \
    "https://api.track.toggl.com/api/v9/me/time_entries/current" | jq

# Get recent time entries (last 7 days by default)
curl -s -u "$TOGGL_API_TOKEN:api_token" \
    "https://api.track.toggl.com/api/v9/me/time_entries" | jq

# Get time entries with date range
START_DATE=$(date -d "7 days ago" +%Y-%m-%dT00:00:00Z)
END_DATE=$(date +%Y-%m-%dT23:59:59Z)

curl -s -u "$TOGGL_API_TOKEN:api_token" \
    "https://api.track.toggl.com/api/v9/me/time_entries?start_date=$START_DATE&end_date=$END_DATE" | jq

# Start a time entry (timer)
curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/time_entries" \
    -d '{
        "created_with": "api",
        "description": "Working on project documentation",
        "tags": ["documentation", "writing"],
        "billable": false,
        "workspace_id": WORKSPACE_ID,
        "project_id": PROJECT_ID,
        "start": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'",
        "duration": -1
    }' | jq

# Stop running time entry
curl -s -X PATCH -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/time_entries/TIME_ENTRY_ID/stop" | jq

# Create completed time entry
curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/time_entries" \
    -d '{
        "created_with": "api",
        "description": "Code review session",
        "workspace_id": WORKSPACE_ID,
        "project_id": PROJECT_ID,
        "start": "2025-01-15T09:00:00.000Z",
        "duration": 3600,
        "tags": ["review", "development"]
    }' | jq

# Update time entry
curl -s -X PUT -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/time_entries/TIME_ENTRY_ID" \
    -d '{
        "description": "Updated description",
        "tags": ["updated-tag"]
    }' | jq

# Delete time entry
curl -s -X DELETE -u "$TOGGL_API_TOKEN:api_token" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/time_entries/TIME_ENTRY_ID"
```

**Python - Toggl Time Entries:**
```python
import requests
from datetime import datetime, timedelta
from base64 import b64encode
import os

class TogglClient:
    """Toggl Track API client."""

    BASE_URL = "https://api.track.toggl.com/api/v9"

    def __init__(self, api_token=None):
        self.api_token = api_token or os.environ.get("TOGGL_API_TOKEN")
        self.auth = (self.api_token, "api_token")

    def _request(self, method, endpoint, data=None):
        """Make API request."""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method,
            url,
            auth=self.auth,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json() if response.text else None

    def get_me(self):
        """Get current user info."""
        return self._request("GET", "/me")

    def get_workspaces(self):
        """Get user's workspaces."""
        return self._request("GET", "/workspaces")

    def get_current_entry(self):
        """Get currently running time entry."""
        return self._request("GET", "/me/time_entries/current")

    def get_time_entries(self, start_date=None, end_date=None):
        """Get time entries within date range."""
        params = []
        if start_date:
            params.append(f"start_date={start_date.isoformat()}Z")
        if end_date:
            params.append(f"end_date={end_date.isoformat()}Z")

        query = f"?{'&'.join(params)}" if params else ""
        return self._request("GET", f"/me/time_entries{query}")

    def start_timer(self, workspace_id, description, project_id=None, tags=None, billable=False):
        """Start a new timer."""
        data = {
            "created_with": "python_api",
            "description": description,
            "workspace_id": workspace_id,
            "billable": billable,
            "start": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "duration": -1  # -1 indicates running timer
        }

        if project_id:
            data["project_id"] = project_id
        if tags:
            data["tags"] = tags

        return self._request(
            "POST",
            f"/workspaces/{workspace_id}/time_entries",
            data
        )

    def stop_timer(self, workspace_id, entry_id):
        """Stop a running timer."""
        return self._request(
            "PATCH",
            f"/workspaces/{workspace_id}/time_entries/{entry_id}/stop"
        )

    def create_time_entry(
        self,
        workspace_id,
        description,
        start_time,
        duration_seconds,
        project_id=None,
        tags=None,
        billable=False
    ):
        """Create a completed time entry."""
        data = {
            "created_with": "python_api",
            "description": description,
            "workspace_id": workspace_id,
            "start": start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "duration": duration_seconds,
            "billable": billable
        }

        if project_id:
            data["project_id"] = project_id
        if tags:
            data["tags"] = tags

        return self._request(
            "POST",
            f"/workspaces/{workspace_id}/time_entries",
            data
        )

    def update_time_entry(self, workspace_id, entry_id, **kwargs):
        """Update an existing time entry."""
        return self._request(
            "PUT",
            f"/workspaces/{workspace_id}/time_entries/{entry_id}",
            kwargs
        )

*Content truncated — see parent skill for full reference.*
