---
name: time-tracking
version: 1.0.0
description: Time tracking integration patterns with RescueTime and Toggl APIs for
  automated time entry, reporting, analytics, and project/task attribution
author: workspace-hub
category: business
type: skill
capabilities:
- Time entry automation
- Project and task attribution
- Productivity analytics
- Reporting and dashboards
- RescueTime API integration
- Toggl Track API integration
- Automated time logging
- Focus time analysis
- Billable hours tracking
- Team time management
tools:
- toggl-api
- rescuetime-api
- curl
- python-requests
tags:
- time-tracking
- toggl
- rescuetime
- productivity
- automation
- reporting
- analytics
- billing
- project-management
platforms:
- rest-api
- python
related_skills:
- todoist-api
- trello-api
- notion-api
- api-integration
requires: []
scripts_exempt: true
---

# Time Tracking

## When to Use This Skill

### USE Time Tracking APIs when:

- **Automating time entries** - Log time from scripts, CI/CD, or other tools
- **Building productivity dashboards** - Aggregate time data for analysis
- **Project billing** - Track billable hours automatically
- **Focus time analysis** - Understand productivity patterns
- **Team time management** - Aggregate team time data
- **Integration pipelines** - Connect time tracking with task managers
- **Automated reporting** - Generate time reports programmatically
- **Custom analytics** - Build specialized productivity insights
### DON'T USE Time Tracking APIs when:

- **Simple manual tracking** - Use native apps instead
- **Real-time monitoring** - APIs have rate limits
- **Invasive employee surveillance** - Ethical concerns
- **Complex invoicing** - Use dedicated billing software

## Prerequisites

### Toggl Track Setup

```bash
# Get API token from:
# https://track.toggl.com/profile (scroll to API Token)

# Set environment variable
export TOGGL_API_TOKEN="your-api-token"

# Toggl uses HTTP Basic Auth with token as username, "api_token" as password
# Or you can use the token directly

# Verify authentication
curl -s -u "$TOGGL_API_TOKEN:api_token" \
    "https://api.track.toggl.com/api/v9/me" | jq '.fullname'
```
### RescueTime Setup

```bash
# Get API Key from:
# https://www.rescuetime.com/anapi/manage

# Set environment variable
export RESCUETIME_API_KEY="your-api-key"

# Verify authentication
curl -s "https://www.rescuetime.com/anapi/data?key=$RESCUETIME_API_KEY&format=json&restrict_kind=overview" | jq
```
### Python Setup

```bash
# Install dependencies
pip install requests python-dateutil pandas

# Using uv
uv pip install requests python-dateutil pandas

# Optional: For Toggl SDK
pip install toggl-python

# Verify
python -c "import requests; print('Ready for time tracking integration!')"
```

## Version History

- **1.0.0** (2026-01-17): Initial release
  - Toggl Track API integration
  - RescueTime API integration
  - Time entry automation
  - Reports and analytics
  - Project attribution
  - Weekly report generator
  - Productivity dashboard
  - GitHub Actions integration
  - Slack integration

## Resources

- **Toggl Track API**: https://engineering.toggl.com/docs/
- **Toggl Reports API**: https://engineering.toggl.com/docs/reports
- **RescueTime API**: https://www.rescuetime.com/anapi/setup/documentation
- **py-toggl**: https://github.com/toggl/toggl_api_docs

---

**Automate your time tracking workflows with Toggl and RescueTime APIs!**

## Sub-Skills

- [1. Toggl Track - Time Entries](1-toggl-track-time-entries/SKILL.md)
- [2. Toggl Track - Projects and Clients](2-toggl-track-projects-and-clients/SKILL.md)
- [3. Toggl Track - Reports](3-toggl-track-reports/SKILL.md)
- [4. RescueTime - Data Retrieval](4-rescuetime-data-retrieval/SKILL.md)
- [5. RescueTime - FocusTime Triggers (+1)](5-rescuetime-focustime-triggers/SKILL.md)
- [Time Tracking with GitHub Actions (+1)](time-tracking-with-github-actions/SKILL.md)
- [1. Handle Rate Limits (+2)](1-handle-rate-limits/SKILL.md)
- [Common Issues](common-issues/SKILL.md)

## Sub-Skills

- [Example 1: Weekly Time Report Generator](example-1-weekly-time-report-generator/SKILL.md)
- [Hours by Day](hours-by-day/SKILL.md)
- [Top Categories (+2)](top-categories/SKILL.md)
