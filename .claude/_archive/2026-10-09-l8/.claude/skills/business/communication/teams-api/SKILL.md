---
name: teams-api
version: 1.0.0
description: Microsoft Teams automation using Graph API, Bot Framework, Adaptive Cards,
  and webhooks for enterprise messaging and collaboration
author: workspace-hub
category: business
type: skill
capabilities:
- graph_api_integration
- bot_framework_development
- adaptive_cards
- messaging_extensions
- webhook_connectors
- channel_management
- meeting_automation
- teams_apps
- proactive_messaging
- notification_workflows
tools:
- microsoft-graph-sdk
- botbuilder-python
- azure-identity
- requests
tags:
- teams
- microsoft
- graph-api
- bot
- adaptive-cards
- enterprise
- messaging
- azure
platforms:
- linux
- macos
- windows
- azure
related_skills:
- slack-api
- github-actions
requires: []
scripts_exempt: true
---

# Teams Api

## When to Use This Skill

### USE when:

- Building bots for Microsoft 365 organizations
- Creating enterprise notification systems
- Integrating with Azure DevOps and Microsoft ecosystem
- Building approval workflows in Teams
- Automating meeting scheduling and management
- Creating messaging extensions for Teams apps
- Implementing compliance-aware messaging solutions
- Building internal tools with Adaptive Cards
### DON'T USE when:

- Organization uses Slack primarily (use slack-api)
- Need simple webhooks only (use incoming webhooks directly)
- No Microsoft 365 subscription available
- Building consumer-facing chat applications
- Need real-time gaming or high-frequency updates

## Prerequisites

### Azure App Registration

```bash
# 1. Go to Azure Portal -> Azure Active Directory -> App registrations
# 2. New registration:
#    - Name: "Teams Bot App"
#    - Supported account types: Accounts in this organizational directory
#    - Redirect URI: Web - https://your-app.azurewebsites.net/auth

# Required API Permissions (Microsoft Graph):
# Application permissions:
# - ChannelMessage.Send           - Send channel messages

*See sub-skills for full details.*
### Python Environment Setup

```bash
# Create virtual environment
python -m venv teams-bot-env
source teams-bot-env/bin/activate  # Linux/macOS

# Install dependencies
pip install azure-identity msgraph-sdk botbuilder-core aiohttp

# Create requirements.txt
cat > requirements.txt << 'EOF'

*See sub-skills for full details.*
### Bot Framework Registration

```bash
# 1. Go to https://dev.botframework.com/bots/new
# 2. Or use Azure Portal -> Create a resource -> Bot Channels Registration

# Bot configuration:
# - Messaging endpoint: https://your-app.azurewebsites.net/api/messages
# - Microsoft App ID: from App Registration
# - Enable Teams channel

# For local development with ngrok:
ngrok http 3978
# Update messaging endpoint to ngrok URL
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive Teams API patterns |

## Resources

- [Microsoft Graph API](https://docs.microsoft.com/graph/)
- [Bot Framework SDK](https://docs.microsoft.com/azure/bot-service/)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Teams App Manifest](https://docs.microsoft.com/microsoftteams/platform/resources/schema/manifest-schema)
- [Teams Webhook Connectors](https://docs.microsoft.com/microsoftteams/platform/webhooks-and-connectors/)

---

*This skill provides production-ready patterns for Microsoft Teams automation, enabling enterprise messaging and collaboration workflows.*

## Sub-Skills

- [1. Microsoft Graph API Client](1-microsoft-graph-api-client/SKILL.md)
- [2. Adaptive Cards](2-adaptive-cards/SKILL.md)
- [3. Incoming Webhooks](3-incoming-webhooks/SKILL.md)
- [4. Bot Framework Integration](4-bot-framework-integration/SKILL.md)
- [5. Proactive Messaging](5-proactive-messaging/SKILL.md)
- [6. Meeting Automation](6-meeting-automation/SKILL.md)
- [Azure DevOps Pipeline Integration (+1)](azure-devops-pipeline-integration/SKILL.md)
- [1. Rate Limiting (+2)](1-rate-limiting/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
