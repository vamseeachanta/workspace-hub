---
name: activepieces
version: 1.0.0
description: Self-hosted no-code automation platform with visual flow builder, type-safe
  custom pieces, API integrations, and event-driven triggers
author: workspace-hub
category: operations
type: skill
capabilities:
- visual_flow_builder
- custom_pieces
- api_integration
- event_triggers
- scheduled_runs
- branching_logic
- loops_iterations
- data_mapping
- webhook_handling
- approval_flows
tools:
- activepieces-cli
- docker
- npm
- node
tags:
- activepieces
- automation
- no-code
- workflow
- integrations
- self-hosted
- open-source
- typescript
platforms:
- linux
- macos
- windows
- docker
- kubernetes
related_skills:
- n8n
- yaml-configuration
- api-integration
- windmill
scripts_exempt: true
see_also:
- activepieces-1-basic-flow-structure
- activepieces-2-webhook-triggers
- activepieces-3-scheduled-flows
- activepieces-4-branching-and-conditional-logic
- activepieces-5-loop-and-iteration
- activepieces-6-custom-piece-development
- activepieces-7-approval-flows
- activepieces-8-error-handling-and-retry-logic
- activepieces-integration-with-notion-and-slack
- activepieces-1-flow-organization
- activepieces-common-issues
---

# Activepieces

## When to Use This Skill

### USE when:

- Building business automations with type-safe custom components
- Self-hosting is required for data sovereignty and compliance
- Need modular, reusable automation pieces
- Creating approval workflows with human-in-the-loop
- Connecting APIs with visual flow builder
- Teams need both no-code and code-first options
- Require MIT-licensed open-source automation
- Building internal tool automations
### DON'T USE when:

- Complex DAG-based data pipeline orchestration (use Airflow)
- CI/CD pipelines tightly coupled with git (use GitHub Actions)
- Need 400+ pre-built integrations immediately (use n8n)
- Sub-second latency requirements (use direct API calls)
- Simple single-trigger cron jobs (use systemd timers)

## Prerequisites

### Installation Options

**Option 1: Docker Compose (Recommended)**
```yaml
# docker-compose.yml
version: '3.8'

services:
  activepieces:
    image: activepieces/activepieces:latest
    restart: always
    ports:

*See sub-skills for full details.*
### Development Setup for Custom Pieces

```bash
# Install Activepieces CLI
npm install -g @activepieces/cli

# Create new piece project
ap create-piece my-custom-piece

# Navigate to piece directory
cd pieces/my-custom-piece


*See sub-skills for full details.*

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive flow patterns |

## Resources

- [Activepieces Documentation](https://www.activepieces.com/docs)
- [Pieces Directory](https://www.activepieces.com/pieces)
- [GitHub Repository](https://github.com/activepieces/activepieces)
- [Community Discord](https://discord.gg/activepieces)
- [Custom Piece Development](https://www.activepieces.com/docs/developers/building-pieces)

---

*This skill provides production-ready patterns for Activepieces workflow automation, tested across enterprise integration scenarios.*

## Sub-Skills

- [1. Basic Flow Structure](1-basic-flow-structure/SKILL.md)
- [2. Webhook Triggers](2-webhook-triggers/SKILL.md)
- [3. Scheduled Flows](3-scheduled-flows/SKILL.md)
- [4. Branching and Conditional Logic](4-branching-and-conditional-logic/SKILL.md)
- [5. Loop and Iteration](5-loop-and-iteration/SKILL.md)
- [6. Custom Piece Development](6-custom-piece-development/SKILL.md)
- [7. Approval Flows](7-approval-flows/SKILL.md)
- [8. Error Handling and Retry Logic](8-error-handling-and-retry-logic/SKILL.md)
- [Integration with Notion and Slack](integration-with-notion-and-slack/SKILL.md)
- [1. Flow Organization (+3)](1-flow-organization/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)
