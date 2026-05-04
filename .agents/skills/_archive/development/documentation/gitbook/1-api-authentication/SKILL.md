---
name: gitbook-1-api-authentication
description: 'Sub-skill of gitbook: 1. API Authentication (+1).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 1. API Authentication (+1)

## 1. API Authentication


**REST API Basics:**
```bash
# GitBook API base URL
API_BASE="https://api.gitbook.com/v1"

# Get current user
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/user" | jq

# List organizations
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/orgs" | jq

# Get organization details
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/orgs/ORG_ID" | jq
```

**Python API Client:**
```python
import requests
from datetime import datetime
import os

class GitBookClient:
    """GitBook API client."""

    BASE_URL = "https://api.gitbook.com/v1"

    def __init__(self, api_token=None):
        self.api_token = api_token or os.environ.get("GITBOOK_API_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, data=None, params=None):
        """Make API request."""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            json=data,
            params=params
        )
        response.raise_for_status()
        return response.json() if response.text else None

    def get_user(self):
        """Get current user."""
        return self._request("GET", "/user")

    def list_organizations(self):
        """List all organizations."""
        return self._request("GET", "/orgs")

    def get_organization(self, org_id):
        """Get organization details."""
        return self._request("GET", f"/orgs/{org_id}")


# Example usage
if __name__ == "__main__":
    client = GitBookClient()

    user = client.get_user()
    print(f"User: {user['displayName']}")

    orgs = client.list_organizations()
    for org in orgs.get("items", []):
        print(f"Org: {org['title']}")
```


## 2. Spaces Management


**REST API - Spaces:**
```bash
# List spaces in organization
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/orgs/ORG_ID/spaces" | jq

# Get space details
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID" | jq

# Create space
curl -s -X POST -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    -H "Content-Type: application/json" \
    "$API_BASE/orgs/ORG_ID/spaces" \
    -d '{
        "title": "API Documentation",
        "visibility": "public"
    }' | jq

# Update space
curl -s -X PATCH -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    -H "Content-Type: application/json" \
    "$API_BASE/spaces/SPACE_ID" \
    -d '{
        "title": "Updated API Documentation",
        "visibility": "private"
    }' | jq

# Delete space
curl -s -X DELETE -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID"

# Get space content (pages)
curl -s -H "Authorization: Bearer $GITBOOK_API_TOKEN" \
    "$API_BASE/spaces/SPACE_ID/content" | jq
```

**Python - Spaces:**
```python
class GitBookClient:
    # ... previous methods ...

    def list_spaces(self, org_id):
        """List all spaces in organization."""
        return self._request("GET", f"/orgs/{org_id}/spaces")

    def get_space(self, space_id):
        """Get space details."""
        return self._request("GET", f"/spaces/{space_id}")

    def create_space(self, org_id, title, visibility="public"):
        """Create a new space."""
        return self._request(
            "POST",
            f"/orgs/{org_id}/spaces",
            data={"title": title, "visibility": visibility}
        )

    def update_space(self, space_id, **kwargs):
        """Update space settings."""
        return self._request(
            "PATCH",
            f"/spaces/{space_id}",
            data=kwargs
        )

    def delete_space(self, space_id):
        """Delete a space."""
        return self._request("DELETE", f"/spaces/{space_id}")

    def get_space_content(self, space_id):
        """Get space content structure."""
        return self._request("GET", f"/spaces/{space_id}/content")


# Example usage
spaces = client.list_spaces("org_xxxxx")
for space in spaces.get("items", []):
    print(f"Space: {space['title']} ({space['visibility']})")

# Create new space
new_space = client.create_space(
    org_id="org_xxxxx",
    title="Developer Guide",
    visibility="public"
)
print(f"Created: {new_space['id']}")
```
