---
name: communication-integration-with-workspace-hub
description: 'Sub-skill of communication: Integration with Workspace-Hub.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Integration with Workspace-Hub

## Integration with Workspace-Hub


These skills enable team communication automation:

```
workspace-hub/
├── scripts/
│   ├── notify-deploy.sh         # Uses: slack-api, teams-api
│   ├── schedule-review.sh       # Uses: calendly-api
│   └── retro-board.sh           # Uses: miro-api
├── automation/
│   ├── slack-bot/               # Uses: slack-api
│   ├── teams-connector/         # Uses: teams-api
│   └── webhooks/
│       ├── slack-handler.sh
│       └── calendly-handler.sh
└── config/
    └── communication.conf       # API tokens and endpoints
```
