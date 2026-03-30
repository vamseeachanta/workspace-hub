---
name: time-tracking-3-toggl-track-reports
description: 'Sub-skill of time-tracking: 3. Toggl Track - Reports.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# 3. Toggl Track - Reports

## 3. Toggl Track - Reports


**Reports API:**
```bash
# Summary report
curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/reports/api/v3/workspace/WORKSPACE_ID/summary/time_entries" \
    -d '{
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "grouping": "projects",
        "sub_grouping": "users"
    }' | jq

# Detailed report
curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/reports/api/v3/workspace/WORKSPACE_ID/search/time_entries" \
    -d '{
        "start_date": "2025-01-01",
        "end_date": "2025-01-31",
        "page_size": 50,
        "first_row_number": 0
    }' | jq

# Weekly report
curl -s -X POST -u "$TOGGL_API_TOKEN:api_token" \
    -H "Content-Type: application/json" \
    "https://api.track.toggl.com/reports/api/v3/workspace/WORKSPACE_ID/weekly/time_entries" \
    -d '{
        "start_date": "2025-01-06",
        "end_date": "2025-01-12",
        "grouping": "projects"
    }' | jq
```

**Python - Reports:**
```python
class TogglReports:
    """Toggl Reports API client."""

    REPORTS_URL = "https://api.track.toggl.com/reports/api/v3"

    def __init__(self, api_token=None):
        self.api_token = api_token or os.environ.get("TOGGL_API_TOKEN")
        self.auth = (self.api_token, "api_token")

    def _request(self, method, endpoint, data=None):
        """Make API request."""
        url = f"{self.REPORTS_URL}{endpoint}"
        response = requests.request(
            method,
            url,
            auth=self.auth,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    def summary_report(
        self,
        workspace_id,
        start_date,
        end_date,
        grouping="projects",
        sub_grouping=None,
        project_ids=None,
        user_ids=None
    ):
        """Generate summary report."""
        data = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "grouping": grouping
        }

        if sub_grouping:
            data["sub_grouping"] = sub_grouping
        if project_ids:
            data["project_ids"] = project_ids
        if user_ids:
            data["user_ids"] = user_ids

        return self._request(
            "POST",
            f"/workspace/{workspace_id}/summary/time_entries",
            data
        )

    def detailed_report(
        self,
        workspace_id,
        start_date,
        end_date,
        page_size=50,
        first_row=0
    ):
        """Generate detailed report with pagination."""
        data = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "page_size": page_size,
            "first_row_number": first_row
        }

        return self._request(
            "POST",
            f"/workspace/{workspace_id}/search/time_entries",
            data
        )

    def weekly_report(
        self,
        workspace_id,
        start_date,
        end_date,
        grouping="projects"
    ):
        """Generate weekly report."""
        data = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "grouping": grouping
        }

        return self._request(
            "POST",
            f"/workspace/{workspace_id}/weekly/time_entries",
            data
        )


# Example usage
if __name__ == "__main__":
    reports = TogglReports()
    workspace_id = 12345678

    # Get summary report
    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 31)

    summary = reports.summary_report(
        workspace_id=workspace_id,
        start_date=start,
        end_date=end,
        grouping="projects"
    )

    print("Summary Report:")
    for group in summary.get("groups", []):
        total_hours = group.get("seconds", 0) / 3600
        print(f"  {group.get('id')}: {total_hours:.1f} hours")
```
