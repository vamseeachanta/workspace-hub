---
name: time-tracking-5-rescuetime-focustime-triggers
description: 'Sub-skill of time-tracking: 5. RescueTime - FocusTime Triggers (+1).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 5. RescueTime - FocusTime Triggers (+1)

## 5. RescueTime - FocusTime Triggers


**FocusTime API:**
```bash
# Start FocusTime session (requires Premium)
curl -s -X POST "https://www.rescuetime.com/anapi/focustime/start" \
    -d "key=$RESCUETIME_API_KEY" \
    -d "duration=60" | jq  # 60 minutes

# End FocusTime session
curl -s -X POST "https://www.rescuetime.com/anapi/focustime/end" \
    -d "key=$RESCUETIME_API_KEY" | jq

# Get current FocusTime status
curl -s "https://www.rescuetime.com/anapi/focustime/status" \
    -d "key=$RESCUETIME_API_KEY" | jq
```

**Python - FocusTime:**
```python
class RescueTimeFocusTime:
    """RescueTime FocusTime API client (Premium required)."""

    BASE_URL = "https://www.rescuetime.com/anapi/focustime"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("RESCUETIME_API_KEY")

    def start_focus(self, duration_minutes=60):
        """Start a FocusTime session."""
        response = requests.post(
            f"{self.BASE_URL}/start",
            data={
                "key": self.api_key,
                "duration": duration_minutes
            }
        )
        return response.json()

    def end_focus(self):
        """End current FocusTime session."""
        response = requests.post(
            f"{self.BASE_URL}/end",
            data={"key": self.api_key}
        )
        return response.json()

    def get_status(self):
        """Get current FocusTime status."""
        response = requests.get(
            f"{self.BASE_URL}/status",
            params={"key": self.api_key}
        )
        return response.json()
```


## 6. Automated Time Logging


**Log Time from Scripts:**
```python
#!/usr/bin/env python3
"""auto_time_logger.py - Automated time logging"""

import os
import subprocess
from datetime import datetime, timedelta
from toggl_client import TogglClient  # From earlier example

def log_git_commit_time(repo_path, workspace_id, project_id=None):
    """
    Log time entries based on git commits.
    Estimates time between commits.
    """
    client = TogglClient()

    # Get recent commits
    result = subprocess.run(
        ["git", "-C", repo_path, "log", "--format=%H|%s|%ai", "-n", "20"],
        capture_output=True,
        text=True
    )

    commits = []
    for line in result.stdout.strip().split("\n"):
        if "|" in line:
            hash_val, message, date_str = line.split("|", 2)
            commit_date = datetime.strptime(
                date_str.strip()[:19],
                "%Y-%m-%d %H:%M:%S"
            )
            commits.append({
                "hash": hash_val,
                "message": message,
                "date": commit_date
            })

    # Create time entries between commits
    for i in range(len(commits) - 1):
        current = commits[i]
        previous = commits[i + 1]

        duration = (current["date"] - previous["date"]).total_seconds()

        # Cap at 4 hours max
        duration = min(duration, 4 * 3600)

        # Skip very short intervals
        if duration < 300:  # Less than 5 minutes
            continue

        entry = client.create_time_entry(
            workspace_id=workspace_id,
            description=f"Git: {current['message'][:100]}",
            start_time=previous["date"],
            duration_seconds=int(duration),
            project_id=project_id,
            tags=["git", "auto-logged"]
        )

        print(f"Logged: {current['message'][:50]}... ({duration/3600:.1f}h)")


def log_pomodoro_session(
    workspace_id,
    description,
    project_id=None,
    duration_minutes=25
):
    """Log a completed Pomodoro session."""
    client = TogglClient()

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=duration_minutes)

    entry = client.create_time_entry(
        workspace_id=workspace_id,
        description=description,
        start_time=start_time,
        duration_seconds=duration_minutes * 60,
        project_id=project_id,
        tags=["pomodoro"]
    )

    print(f"Logged Pomodoro: {description} ({duration_minutes} min)")
    return entry


def log_meeting(
    workspace_id,
    title,
    start_time,
    end_time,
    project_id=None
):
    """Log a meeting time entry."""
    client = TogglClient()

    duration = (end_time - start_time).total_seconds()

    entry = client.create_time_entry(
        workspace_id=workspace_id,
        description=f"Meeting: {title}",
        start_time=start_time,
        duration_seconds=int(duration),
        project_id=project_id,
        tags=["meeting"]
    )

    print(f"Logged meeting: {title} ({duration/3600:.1f}h)")
    return entry
```
