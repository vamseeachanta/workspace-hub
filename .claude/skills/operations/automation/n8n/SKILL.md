---
name: n8n
version: 1.0.0
description: Open-source workflow automation platform with visual node-based editor,
  400+ integrations, webhooks, and self-hosted deployment capabilities
author: workspace-hub
category: operations
type: skill
capabilities:
- visual_workflow_builder
- webhook_triggers
- scheduled_execution
- api_integrations
- custom_nodes
- credentials_management
- workflow_templates
- error_handling
- data_transformation
- conditional_logic
tools:
- n8n-cli
- docker
- npm
- node
tags:
- n8n
- workflow
- automation
- integrations
- webhooks
- low-code
- self-hosted
- etl
- data-pipeline
platforms:
- linux
- macos
- windows
- docker
- kubernetes
related_skills:
- yaml-configuration
- api-integration
- github-actions
- activepieces
- windmill
scripts_exempt: true
---

# N8N

## When to Use This Skill

### USE when:

- Building integrations between 400+ services (Slack, Gmail, Notion, Airtable, etc.)
- Creating visual workflows accessible to non-developers
- Self-hosting is required for data sovereignty and compliance
- Need webhook-triggered automations with real-time processing
- Building internal tool automations and business process automation
- Connecting APIs without writing extensive code
- Rapid prototyping of automation workflows
- Need human-in-the-loop approval workflows
### DON'T USE when:

- Orchestrating complex data pipelines with dependencies (use Airflow)
- CI/CD pipelines tightly coupled with git (use GitHub Actions)
- Need sub-second latency requirements (use direct API calls)
- Processing massive datasets (use dedicated ETL tools)
- Require enterprise audit compliance out-of-box (evaluate requirements)
- Simple single-trigger cron jobs (use systemd timers)

## Prerequisites

### Installation Options

**Option 1: npm (Development)**
```bash
# Install globally
npm install n8n -g

# Start n8n
n8n start

# Access UI at http://localhost:5678
```

*See sub-skills for full details.*
### Development Setup

```bash
# Clone for custom node development
git clone https://github.com/n8n-io/n8n.git
cd n8n

# Install dependencies
pnpm install

# Build
pnpm build

# Start development server
pnpm dev
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive workflow patterns |

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [n8n Workflow Templates](https://n8n.io/workflows/)
- [n8n GitHub Repository](https://github.com/n8n-io/n8n)
- [Custom Node Development](https://docs.n8n.io/integrations/creating-nodes/)
- [n8n API Reference](https://docs.n8n.io/api/)

---

*This skill provides production-ready patterns for n8n workflow automation, tested across enterprise integration scenarios handling thousands of daily executions.*

## Sub-Skills

- [1. Basic Workflow Structure](1-basic-workflow-structure/SKILL.md)
- [2. Webhook Triggers](2-webhook-triggers/SKILL.md)
- [3. Scheduled Workflows](3-scheduled-workflows/SKILL.md)
- [4. Conditional Branching and Error Handling](4-conditional-branching-and-error-handling/SKILL.md)
- [5. Data Transformation with Code Node (+1)](5-data-transformation-with-code-node/SKILL.md)
- [7. Custom Node Development](7-custom-node-development/SKILL.md)
- [8. Workflow Templates and Subworkflows](8-workflow-templates-and-subworkflows/SKILL.md)
- [Integration with Slack, Google Sheets, and Email](integration-with-slack-google-sheets-and-email/SKILL.md)
- [Integration with GitHub and Jira](integration-with-github-and-jira/SKILL.md)
- [1. Workflow Organization (+4)](1-workflow-organization/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)
