---
name: slack-api
version: 1.0.0
description: Slack bot development and workspace automation using Web API, Events
  API, Socket Mode, and Block Kit for building interactive messaging applications
author: workspace-hub
category: business
type: skill
capabilities:
- web_api_integration
- events_api_handling
- socket_mode_connections
- block_kit_messages
- interactive_components
- slash_commands
- modals_and_views
- workflow_automation
- message_threading
- file_sharing
tools:
- slack-bolt-python
- slack-sdk
- ngrok
- curl
tags:
- slack
- bot
- api
- messaging
- automation
- webhooks
- block-kit
- events
- python
platforms:
- linux
- macos
- windows
related_skills:
- teams-api
- github-actions
- python-scientific-computing
requires: []
scripts_exempt: true
---

# Slack Api

## When to Use This Skill

### USE when:

- Building notification systems for CI/CD pipelines
- Creating interactive bots for team workflows
- Automating incident response and alerting
- Building approval workflows with interactive messages
- Integrating external services with Slack channels
- Creating slash commands for common operations
- Building internal tools with modal dialogs
- Implementing scheduled message automation
### DON'T USE when:

- Microsoft Teams is the primary platform (use teams-api)
- Simple one-way notifications only (use incoming webhooks directly)
- Need email-based workflows (different domain)
- Slack Enterprise Grid with complex org requirements
- Real-time gaming or high-frequency updates (consider WebSockets)

## Prerequisites

### Slack App Setup

```bash
# 1. Create a Slack App at https://api.slack.com/apps
# 2. Choose "From scratch" and select your workspace

# Required Bot Token Scopes (OAuth & Permissions):
# - chat:write          - Post messages
# - chat:write.public   - Post to channels without joining
# - channels:read       - List public channels
# - channels:history    - Read channel messages
# - groups:read         - List private channels

*See sub-skills for full details.*
### Python Environment Setup

```bash
# Create virtual environment
python -m venv slack-bot-env
source slack-bot-env/bin/activate  # Linux/macOS
# slack-bot-env\Scripts\activate   # Windows

# Install Slack Bolt SDK
pip install slack-bolt slack-sdk

# Install additional dependencies

*See sub-skills for full details.*
### Local Development with ngrok

```bash
# Install ngrok
brew install ngrok  # macOS
# Or download from https://ngrok.com/download

# Authenticate ngrok
ngrok config add-authtoken YOUR_AUTH_TOKEN

# Start tunnel for local development
ngrok http 3000

*See sub-skills for full details.*

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive Slack API patterns |

## Resources

- [Slack API Documentation](https://api.slack.com/)
- [Bolt for Python](https://slack.dev/bolt-python/)
- [Block Kit Builder](https://app.slack.com/block-kit-builder/)
- [Slack App Manifest](https://api.slack.com/reference/manifests)
- [Socket Mode](https://api.slack.com/apis/connections/socket)
- [Events API](https://api.slack.com/events-api)

---

*This skill provides production-ready patterns for Slack bot development, enabling powerful team automation and interactive workflows.*

## Sub-Skills

- [1. Basic Slack Bot with Bolt](1-basic-slack-bot-with-bolt/SKILL.md)
- [2. Block Kit Messages](2-block-kit-messages/SKILL.md)
- [3. Interactive Components and Actions](3-interactive-components-and-actions/SKILL.md)
- [4. Modals and Views](4-modals-and-views/SKILL.md)
- [5. Slash Commands](5-slash-commands/SKILL.md)
- [6. Webhooks and Incoming Messages](6-webhooks-and-incoming-messages/SKILL.md)
- [GitHub Actions Integration (+1)](github-actions-integration/SKILL.md)
- [1. Rate Limiting (+3)](1-rate-limiting/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)
