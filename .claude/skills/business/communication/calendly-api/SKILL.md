---
name: calendly-api
version: 1.0.0
description: Calendly scheduling automation using REST API v2 for managing event types,
  availability, bookings, webhooks, and scheduling workflows
author: workspace-hub
category: business
type: skill
capabilities:
- event_type_management
- availability_scheduling
- booking_management
- webhook_subscriptions
- invitee_tracking
- routing_forms
- organization_management
- user_scheduling
- cancellation_handling
- scheduling_links
tools:
- curl
- requests
- httpx
- python
tags:
- calendly
- scheduling
- calendar
- booking
- meetings
- api
- automation
- webhooks
platforms:
- linux
- macos
- windows
related_skills:
- slack-api
- teams-api
- github-actions
requires: []
see_also:
- calendly-api-1-user-and-organization-management
- calendly-api-2-event-types
- calendly-api-3-scheduled-events
- calendly-api-4-invitees
- calendly-api-5-webhooks
- calendly-api-6-scheduling-links-and-routing
- calendly-api-slack-notification-integration
- calendly-api-github-actions-integration
- calendly-api-1-rate-limiting
- calendly-api-common-issues
scripts_exempt: true
---

# Calendly Api

## When to Use This Skill

### USE when:

- Automating interview scheduling workflows
- Building meeting booking integrations
- Creating round-robin scheduling systems
- Tracking scheduled events programmatically
- Integrating calendars with CRM systems
- Building appointment reminders
- Creating custom booking confirmation flows
- Automating follow-up sequences after meetings
- Syncing Calendly with external calendars
- Building scheduling analytics dashboards
### DON'T USE when:

- Simple calendar display (use Google Calendar API)
- Real-time video calls (use Zoom/Teams API)
- Complex resource scheduling (use specialized tools)
- Internal meeting coordination only (use calendar apps)
- One-off manual scheduling (use Calendly UI directly)

## Prerequisites

### Calendly API Setup

```bash
# 1. Get API credentials at https://calendly.com/integrations/api_webhooks
# 2. Create a Personal Access Token or OAuth app
# 3. Note: API v2 requires organization-level access for some endpoints

# Personal Access Token:
# - Go to Integrations > API & Webhooks
# - Generate a new token
# - Copy the token (shown only once)


*See sub-skills for full details.*
### Python Environment Setup

```bash
# Create virtual environment
python -m venv calendly-env
source calendly-env/bin/activate  # Linux/macOS
# calendly-env\Scripts\activate   # Windows

# Install dependencies
pip install requests python-dotenv httpx aiohttp

# Create requirements.txt

*See sub-skills for full details.*
### API Client Setup

```python
# client.py
# ABOUTME: Calendly API client with authentication
# ABOUTME: Handles requests, pagination, and error handling

import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv


*See sub-skills for full details.*

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive Calendly API v2 patterns |

## Resources

- [Calendly API Documentation](https://developer.calendly.com/api-docs)
- [Calendly Developer Portal](https://developer.calendly.com/)
- [OAuth 2.0 Guide](https://developer.calendly.com/getting-started-with-oauth)
- [Webhooks Guide](https://developer.calendly.com/api-docs/4e4e9a77ef8bc-webhooks)
- [Rate Limits](https://developer.calendly.com/api-docs/rate-limiting)
- [API Changelog](https://developer.calendly.com/api-changelog)

---

*This skill provides production-ready patterns for Calendly scheduling automation, enabling seamless meeting coordination and booking workflows.*

## Sub-Skills

- [1. User and Organization Management](1-user-and-organization-management/SKILL.md)
- [2. Event Types](2-event-types/SKILL.md)
- [3. Scheduled Events](3-scheduled-events/SKILL.md)
- [4. Invitees](4-invitees/SKILL.md)
- [5. Webhooks](5-webhooks/SKILL.md)
- [6. Scheduling Links and Routing](6-scheduling-links-and-routing/SKILL.md)
- [Slack Notification Integration](slack-notification-integration/SKILL.md)
- [GitHub Actions Integration](github-actions-integration/SKILL.md)
- [1. Rate Limiting (+3)](1-rate-limiting/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)
