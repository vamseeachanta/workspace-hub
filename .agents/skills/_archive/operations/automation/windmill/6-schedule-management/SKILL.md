---
name: windmill-6-schedule-management
description: 'Sub-skill of windmill: 6. Schedule Management.'
version: 1.0.0
category: operations
type: reference
scripts_exempt: true
---

# 6. Schedule Management

## 6. Schedule Management


```python
# scripts/scheduling/dynamic_scheduler.py
"""
Dynamically manage schedules based on business rules.
"""

import wmill
from datetime import datetime, timedelta
from typing import List, Optional


def main(
    schedule_configs: List[dict],
    dry_run: bool = True,
):
    """
    Update Windmill schedules based on configuration.

    Args:
        schedule_configs: List of schedule configurations
        dry_run: If True, only report what would change

    Returns:
        Summary of schedule changes
    """
    client = wmill.Client()
    workspace = wmill.get_workspace()

    changes = []

    for config in schedule_configs:
        schedule_path = config["path"]
        enabled = config.get("enabled", True)
        cron = config.get("cron")
        timezone = config.get("timezone", "UTC")

        # Check business hours constraint
        if config.get("business_hours_only", False):
            # Modify cron to only run during business hours (9-17)
            if cron:
                cron_parts = cron.split()
                if len(cron_parts) >= 5:
                    cron_parts[1] = "9-17"  # Hours
                    cron_parts[4] = "1-5"   # Weekdays only
                    cron = " ".join(cron_parts)

        # Check maintenance window constraint
        if config.get("skip_maintenance_windows", False):
            maintenance = get_maintenance_windows()
            now = datetime.now()
            in_maintenance = any(
                m["start"] <= now <= m["end"]
                for m in maintenance
            )
            if in_maintenance:
                enabled = False

        change = {
            "path": schedule_path,
            "cron": cron,
            "timezone": timezone,
            "enabled": enabled,
            "dry_run": dry_run
        }

        if not dry_run:
            # Update schedule via Windmill API
            try:
                client.update_schedule(
                    workspace=workspace,
                    path=schedule_path,
                    schedule={
                        "schedule": cron,
                        "timezone": timezone,
                        "enabled": enabled
                    }
                )
                change["status"] = "updated"
            except Exception as e:
                change["status"] = "error"
                change["error"] = str(e)
        else:
            change["status"] = "would_update"

        changes.append(change)

    return {
        "total_schedules": len(schedule_configs),
        "changes": changes,
        "dry_run": dry_run
    }


def get_maintenance_windows():
    """Fetch maintenance windows from configuration."""
    try:
        config = wmill.get_variable("u/admin/maintenance_windows")
        return config.get("windows", [])
    except:
        return []
```
