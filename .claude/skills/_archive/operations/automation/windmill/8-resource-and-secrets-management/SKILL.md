---
name: windmill-8-resource-and-secrets-management
description: 'Sub-skill of windmill: 8. Resource and Secrets Management.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 8. Resource and Secrets Management

## 8. Resource and Secrets Management


```python
# scripts/admin/manage_resources.py
"""
Manage Windmill resources and secrets programmatically.
"""

import wmill
from typing import Optional


def main(
    action: str,  # "list", "get", "create", "update", "delete"
    resource_path: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_value: Optional[dict] = None,
    description: Optional[str] = None,
):
    """
    Manage Windmill resources (secrets, connections, configs).

    Args:
        action: Operation to perform
        resource_path: Path to resource (e.g., "u/admin/my_api")
        resource_type: Type of resource (for create)
        resource_value: Resource value (for create/update)
        description: Resource description

    Returns:
        Operation result
    """
    workspace = wmill.get_workspace()

    if action == "list":
        # List all resources in workspace
        resources = wmill.list_resources()
        return {
            "total": len(resources),
            "resources": [
                {
                    "path": r["path"],
                    "resource_type": r.get("resource_type"),
                    "description": r.get("description", "")
                }
                for r in resources
            ]
        }

    elif action == "get":
        if not resource_path:
            raise ValueError("resource_path required for get action")

        try:
            value = wmill.get_resource(resource_path)
            return {
                "path": resource_path,
                "value": value,
                "found": True
            }
        except Exception as e:
            return {
                "path": resource_path,
                "found": False,
                "error": str(e)
            }

    elif action == "create":
        if not all([resource_path, resource_type, resource_value]):
            raise ValueError("resource_path, resource_type, and resource_value required for create")

        # Validate resource type exists
        valid_types = ["postgresql", "mysql", "mongodb", "s3", "smtp", "slack", "http"]
        if resource_type not in valid_types and not resource_type.startswith("c/"):
            print(f"Warning: Unknown resource type '{resource_type}'")

        # Create resource via API
        result = wmill.create_resource(
            path=resource_path,
            resource_type=resource_type,
            value=resource_value,
            description=description or ""
        )

        return {
            "action": "created",
            "path": resource_path,
            "resource_type": resource_type,
            "success": True
        }

    elif action == "update":
        if not all([resource_path, resource_value]):
            raise ValueError("resource_path and resource_value required for update")

        result = wmill.update_resource(
            path=resource_path,
            value=resource_value
        )

        return {
            "action": "updated",
            "path": resource_path,
            "success": True
        }

    elif action == "delete":
        if not resource_path:
            raise ValueError("resource_path required for delete")

        result = wmill.delete_resource(path=resource_path)

        return {
            "action": "deleted",
            "path": resource_path,
            "success": True
        }

    else:
        raise ValueError(f"Unknown action: {action}")
```
