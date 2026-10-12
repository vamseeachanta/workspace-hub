---
name: miro-api
version: 1.0.0
description: Miro whiteboard automation using REST API v2 and Python SDK for creating
  boards, frames, shapes, connectors, and collaborative visual workflows
author: workspace-hub
category: business
type: skill
capabilities:
- board_management
- sticky_notes_creation
- shape_drawing
- connector_lines
- frame_organization
- text_elements
- image_embedding
- template_usage
- real_time_collaboration
- webhook_subscriptions
tools:
- miro-api-python
- curl
- requests
- httpx
tags:
- miro
- whiteboard
- collaboration
- visual
- diagrams
- sticky-notes
- api
- python
platforms:
- linux
- macos
- windows
related_skills:
- slack-api
- notion-api
- github-actions
requires: []
scripts_exempt: true
---

# Miro Api

## When to Use This Skill

### USE when:

- Automating sprint retrospective board creation
- Building visual project status dashboards
- Creating automated architecture diagrams
- Setting up templated workshop boards
- Integrating Miro with CI/CD pipelines
- Automating user story mapping workflows
- Creating visual incident response boards
- Building automated onboarding boards
- Generating meeting facilitation templates
- Syncing data from external systems to Miro
### DON'T USE when:

- Simple text-based collaboration (use Slack or Teams)
- Document-focused workflows (use Notion or Confluence)
- Code-focused diagramming (use Mermaid or PlantUML)
- Real-time whiteboarding without persistence
- Personal note-taking (use Obsidian)

## Prerequisites

### Miro App Setup

```bash
# 1. Create a Miro App at https://miro.com/app/settings/user-profile/apps
# 2. Choose REST API 2.0
# 3. Configure OAuth 2.0 scopes

# Required OAuth Scopes:
# - boards:read          - Read board data
# - boards:write         - Create and modify boards
# - team:read            - Read team information
# - identity:read        - Read user identity

*See sub-skills for full details.*
### Python Environment Setup

```bash
# Create virtual environment
python -m venv miro-env
source miro-env/bin/activate  # Linux/macOS
# miro-env\Scripts\activate   # Windows

# Install Miro API SDK
pip install miro-api

# Install additional dependencies

*See sub-skills for full details.*
### API Authentication

```python
# auth.py
# ABOUTME: Miro API authentication utilities
# ABOUTME: Handles OAuth2 token management and refresh

import os
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta


*See sub-skills for full details.*

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive Miro API v2 patterns |

## Resources

- [Miro REST API Documentation](https://developers.miro.com/reference)
- [Miro Python SDK](https://github.com/miroapp/api-clients)
- [Miro Developer Portal](https://developers.miro.com/)
- [OAuth 2.0 Guide](https://developers.miro.com/docs/getting-started-with-oauth)
- [Webhooks Documentation](https://developers.miro.com/docs/webhooks)
- [Rate Limits](https://developers.miro.com/docs/rate-limiting)

---

*This skill provides production-ready patterns for Miro whiteboard automation, enabling powerful visual collaboration workflows and team productivity tools.*

## Sub-Skills

- [1. Board Management](1-board-management/SKILL.md)
- [2. Sticky Notes and Cards](2-sticky-notes-and-cards/SKILL.md)
- [3. Shapes and Drawing](3-shapes-and-drawing/SKILL.md)
- [4. Connectors and Lines](4-connectors-and-lines/SKILL.md)
- [5. Frames and Organization](5-frames-and-organization/SKILL.md)
- [6. Text and Images](6-text-and-images/SKILL.md)
- [GitHub Actions Integration](github-actions-integration/SKILL.md)
- [Sprint Retrospective Automation](sprint-retrospective-automation/SKILL.md)
- [1. Rate Limiting (+3)](1-rate-limiting/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)
