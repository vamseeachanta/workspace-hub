---
name: calendly-api-1-user-and-organization-management
description: 'Sub-skill of calendly-api: 1. User and Organization Management.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 1. User and Organization Management

## 1. User and Organization Management


```python
# users.py
# ABOUTME: User and organization management
# ABOUTME: Retrieve user profiles, organization info, memberships

from client import client


def get_current_user() -> dict:
    """Get the current authenticated user"""
    response = client.get("/users/me")
    user = response.get("resource", {})

    return {
        "uri": user.get("uri"),
        "name": user.get("name"),
        "email": user.get("email"),
        "slug": user.get("slug"),
        "scheduling_url": user.get("scheduling_url"),
        "timezone": user.get("timezone"),
        "organization": user.get("current_organization"),
    }


def get_user_by_uri(user_uri: str) -> dict:
    """Get a user by their URI"""
    # Extract UUID from URI
    uuid = user_uri.split("/")[-1]
    response = client.get(f"/users/{uuid}")
    return response.get("resource", {})


def get_organization(organization_uri: str = None) -> dict:
    """Get organization details"""
    org_uri = organization_uri or client.organization_uri
    uuid = org_uri.split("/")[-1]
    response = client.get(f"/organizations/{uuid}")
    return response.get("resource", {})


def list_organization_memberships(
    organization_uri: str = None,
    email: str = None,
) -> list:
    """List organization memberships"""
    org_uri = organization_uri or client.organization_uri

    params = {"organization": org_uri}
    if email:
        params["email"] = email

    return client.paginate("/organization_memberships", params=params)


def get_user_availability_schedules(user_uri: str = None) -> list:
    """Get user's availability schedules"""
    user = user_uri or client.user_uri
    params = {"user": user}
    return client.paginate("/user_availability_schedules", params=params)


def get_user_busy_times(
    user_uri: str = None,
    start_time: str = None,
    end_time: str = None,
) -> list:
    """Get user's busy times for a date range

    Times should be ISO 8601 format: 2026-01-17T00:00:00Z
    """
    user = user_uri or client.user_uri
    params = {
        "user": user,
        "start_time": start_time,
        "end_time": end_time,
    }
    response = client.get("/user_busy_times", params=params)
    return response.get("collection", [])


if __name__ == "__main__":
    # Get current user
    user = get_current_user()
    print(f"User: {user['name']} ({user['email']})")
    print(f"Scheduling URL: {user['scheduling_url']}")

    # List memberships
    memberships = list_organization_memberships()
    print(f"\nOrganization has {len(memberships)} members")
```
