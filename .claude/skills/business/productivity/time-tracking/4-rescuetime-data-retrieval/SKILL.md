---
name: time-tracking-4-rescuetime-data-retrieval
description: 'Sub-skill of time-tracking: 4. RescueTime - Data Retrieval.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 4. RescueTime - Data Retrieval

## 4. RescueTime - Data Retrieval


**REST API - Analytics:**
```bash
# Get summary data
curl -s "https://www.rescuetime.com/anapi/data" \
    -d "key=$RESCUETIME_API_KEY" \
    -d "format=json" \
    -d "perspective=rank" \
    -d "resolution_time=day" \
    -d "restrict_kind=overview" | jq

# Get data for specific date range
curl -s "https://www.rescuetime.com/anapi/data" \
    -d "key=$RESCUETIME_API_KEY" \
    -d "format=json" \
    -d "restrict_begin=2025-01-01" \
    -d "restrict_end=2025-01-31" \
    -d "restrict_kind=overview" | jq

# Get activity data by category
curl -s "https://www.rescuetime.com/anapi/data" \
    -d "key=$RESCUETIME_API_KEY" \
    -d "format=json" \
    -d "restrict_kind=category" \
    -d "resolution_time=week" | jq

# Get productivity data
curl -s "https://www.rescuetime.com/anapi/data" \
    -d "key=$RESCUETIME_API_KEY" \
    -d "format=json" \
    -d "restrict_kind=productivity" | jq

# Get activity details
curl -s "https://www.rescuetime.com/anapi/data" \
    -d "key=$RESCUETIME_API_KEY" \
    -d "format=json" \
    -d "restrict_kind=activity" \
    -d "resolution_time=day" | jq

# Get efficiency data (requires Premium)
curl -s "https://www.rescuetime.com/anapi/data" \
    -d "key=$RESCUETIME_API_KEY" \
    -d "format=json" \
    -d "restrict_kind=efficiency" | jq
```

**Python - RescueTime Client:**
```python
import requests
from datetime import datetime, timedelta
import os

class RescueTimeClient:
    """RescueTime API client."""

    BASE_URL = "https://www.rescuetime.com/anapi"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("RESCUETIME_API_KEY")

    def _request(self, endpoint, params=None):
        """Make API request."""
        params = params or {}
        params["key"] = self.api_key
        params["format"] = "json"

        response = requests.get(
            f"{self.BASE_URL}/{endpoint}",
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_daily_summary(self, date=None):
        """Get daily summary data."""
        params = {
            "perspective": "rank",
            "resolution_time": "day",
            "restrict_kind": "overview"
        }

        if date:
            params["restrict_begin"] = date.strftime("%Y-%m-%d")
            params["restrict_end"] = date.strftime("%Y-%m-%d")

        return self._request("data", params)

    def get_date_range_data(
        self,
        start_date,
        end_date,
        restrict_kind="overview",
        resolution="day"
    ):
        """Get data for date range."""
        params = {
            "restrict_begin": start_date.strftime("%Y-%m-%d"),
            "restrict_end": end_date.strftime("%Y-%m-%d"),
            "restrict_kind": restrict_kind,
            "resolution_time": resolution
        }

        return self._request("data", params)

    def get_productivity_data(self, start_date=None, end_date=None):
        """Get productivity scores."""
        params = {"restrict_kind": "productivity"}

        if start_date:
            params["restrict_begin"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["restrict_end"] = end_date.strftime("%Y-%m-%d")

        return self._request("data", params)

    def get_category_data(
        self,
        start_date=None,
        end_date=None,
        resolution="day"
    ):
        """Get data grouped by category."""
        params = {
            "restrict_kind": "category",
            "resolution_time": resolution
        }

        if start_date:
            params["restrict_begin"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["restrict_end"] = end_date.strftime("%Y-%m-%d")

        return self._request("data", params)

    def get_activity_data(
        self,
        start_date=None,
        end_date=None,
        resolution="day"
    ):
        """Get detailed activity data."""
        params = {
            "restrict_kind": "activity",
            "resolution_time": resolution
        }

        if start_date:
            params["restrict_begin"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["restrict_end"] = end_date.strftime("%Y-%m-%d")

        return self._request("data", params)

    def get_focus_time(self, start_date=None, end_date=None):
        """Calculate focus time from activities."""
        productivity = self.get_productivity_data(start_date, end_date)

        focus_time = 0
        total_time = 0

        for row in productivity.get("rows", []):
            # row format: [rank, time_seconds, productivity]
            time_seconds = row[1]
            productivity_score = row[2]  # -2 to 2

            total_time += time_seconds
            if productivity_score >= 1:  # Productive or very productive
                focus_time += time_seconds

        return {
            "focus_time_seconds": focus_time,
            "focus_time_hours": focus_time / 3600,
            "total_time_seconds": total_time,
            "total_time_hours": total_time / 3600,
            "focus_percentage": (focus_time / total_time * 100) if total_time > 0 else 0
        }


# Example usage
if __name__ == "__main__":
    client = RescueTimeClient()

    # Get today's summary
    today = client.get_daily_summary()
    print("Today's Activity:")

*Content truncated — see parent skill for full reference.*
