---
name: time-tracking-2-toggl-track-projects-and-clients
description: 'Sub-skill of time-tracking: 2. Toggl Track - Projects and Clients.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 2. Toggl Track - Projects and Clients

## 2. Toggl Track - Projects and Clients


**REST API - Projects:**
```bash
# Get workspace projects
curl -s -u "$TOGGL_API_TOKEN:api_token" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/projects" | jq

# Create project
curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/projects" \
    -d '{
        "name": "Client Website Redesign",
        "color": "#0b83d9",
        "is_private": false,
        "active": true,
        "client_id": CLIENT_ID,
        "billable": true,
        "estimated_hours": 100
    }' | jq

# Get clients
curl -s -u "$TOGGL_API_TOKEN:api_token" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/clients" | jq

# Create client
curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/clients" \
    -d '{
        "name": "Acme Corporation",
        "notes": "Primary contact: John Doe"
    }' | jq

# Get tags
curl -s -u "$TOGGL_API_TOKEN:api_token" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/tags" | jq

# Create tag
curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/api/v9/workspaces/WORKSPACE_ID/tags" \
    -d '{"name": "urgent"}' | jq
```

**Python - Projects and Clients:**
```python
def get_projects(self, workspace_id):
    """Get all projects in workspace."""
    return self._request("GET", f"/workspaces/{workspace_id}/projects")

def create_project(
    self,
    workspace_id,
    name,
    client_id=None,
    color="#0b83d9",
    billable=False,
    estimated_hours=None
):
    """Create a new project."""
    data = {
        "name": name,
        "color": color,
        "billable": billable,
        "active": True
    }

    if client_id:
        data["client_id"] = client_id
    if estimated_hours:
        data["estimated_hours"] = estimated_hours

    return self._request(
        "POST",
        f"/workspaces/{workspace_id}/projects",
        data
    )

def get_clients(self, workspace_id):
    """Get all clients in workspace."""
    return self._request("GET", f"/workspaces/{workspace_id}/clients")

def create_client(self, workspace_id, name, notes=None):
    """Create a new client."""
    data = {"name": name}
    if notes:
        data["notes"] = notes

    return self._request(
        "POST",
        f"/workspaces/{workspace_id}/clients",
        data
    )
```
