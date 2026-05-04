---
name: calendly-api-github-actions-integration
description: 'Sub-skill of calendly-api: GitHub Actions Integration.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# GitHub Actions Integration

## GitHub Actions Integration


```yaml
# .github/workflows/calendly-sync.yml
name: Sync Calendly Events

on:
  schedule:
    - cron: '0 8 * * *'  # Daily at 8 AM
  workflow_dispatch:

jobs:
  sync-events:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install requests

      - name: Fetch upcoming events
        env:
          CALENDLY_API_KEY: ${{ secrets.CALENDLY_API_KEY }}
        run: |
          python << 'EOF'
          import os
          import requests
          from datetime import datetime, timedelta
          import json

          API_KEY = os.environ["CALENDLY_API_KEY"]
          BASE_URL = "https://api.calendly.com"

          headers = {
              "Authorization": f"Bearer {API_KEY}",
              "Content-Type": "application/json",
          }

          # Get current user
          user_response = requests.get(f"{BASE_URL}/users/me", headers=headers)
          user = user_response.json()["resource"]
          user_uri = user["uri"]

          # Get upcoming events
          now = datetime.utcnow()
          end = now + timedelta(days=7)

          params = {
              "user": user_uri,
              "min_start_time": now.isoformat() + "Z",
              "max_start_time": end.isoformat() + "Z",
              "status": "active",
          }

          events_response = requests.get(
              f"{BASE_URL}/scheduled_events",
              headers=headers,
              params=params,
          )
          events = events_response.json()["collection"]

          print(f"Found {len(events)} upcoming events")

          # Save to file
          with open("upcoming_events.json", "w") as f:
              json.dump(events, f, indent=2)

          # Create summary
          summary = []
          for event in events:
              summary.append({
                  "name": event["name"],
                  "start_time": event["start_time"],
                  "status": event["status"],
              })

          with open("events_summary.json", "w") as f:
              json.dump(summary, f, indent=2)

          print("Events synced successfully")
          EOF

      - name: Upload events artifact
        uses: actions/upload-artifact@v4
        with:
          name: calendly-events
          path: |
            upcoming_events.json
            events_summary.json
```
