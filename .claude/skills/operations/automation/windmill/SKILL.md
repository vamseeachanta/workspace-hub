---
name: windmill
version: 1.0.0
description: Developer-first workflow engine that turns scripts into workflows and
  UIs, supporting Python, TypeScript, Go, and Bash with approval flows, schedule management,
  and self-hosted deployment
author: workspace-hub
category: operations
type: skill
capabilities:
- script_to_workflow
- auto_generated_ui
- approval_flows
- schedule_management
- python_typescript_go
- flow_orchestration
- webhook_triggers
- resource_management
- secrets_management
- branching_logic
tools:
- windmill-cli
- docker
- python
- node
- deno
tags:
- windmill
- workflow
- automation
- scripts
- python
- typescript
- go
- bash
- self-hosted
- developer-tools
platforms:
- linux
- macos
- windows
- docker
- kubernetes
related_skills:
- n8n
- activepieces
- airflow
- yaml-configuration
scripts_exempt: true
see_also:
- windmill-1-python-scripts
- windmill-2-typescriptdeno-scripts
- windmill-3-go-scripts
- windmill-4-bash-scripts
- windmill-5-flow-orchestration
- windmill-6-schedule-management
- windmill-7-approval-flows
- windmill-8-resource-and-secrets-management
- windmill-integration-with-database-and-slack
- windmill-1-script-organization
- windmill-common-issues
---

# Windmill

## When to Use This Skill

### USE when:

- Developers prefer writing code over visual tools
- Need auto-generated UIs for script parameters
- Building internal tools with minimal frontend work
- Python, TypeScript, Go, or Bash are primary languages
- Combining workflow automation with internal tools
- Need code review and version control for automations
- Require approval flows with audit trails
- Self-hosting for data sovereignty
### DON'T USE when:

- Non-developers need to build workflows (use n8n, Activepieces)
- Need 400+ pre-built integrations (use n8n)
- Complex DAG orchestration with dependencies (use Airflow)
- CI/CD pipelines tightly coupled with git (use GitHub Actions)
- Simple visual automation preferred (use Activepieces)

## Prerequisites

### Installation Options

**Option 1: Docker Compose (Recommended)**
```yaml
# docker-compose.yml
version: '3.8'

services:
  windmill:
    image: ghcr.io/windmill-labs/windmill:main
    restart: always
    ports:

*See sub-skills for full details.*
### Development Setup

```bash
# Install language-specific dependencies

# Python development
pip install wmill pandas numpy requests

# TypeScript/Deno development
# Windmill uses Deno runtime for TypeScript
deno --version

# Go development
go install github.com/windmill-labs/windmill-go-client@latest

# Bash scripts work out of the box
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-17 | Initial release with comprehensive workflow patterns |

## Resources

- [Windmill Documentation](https://www.windmill.dev/docs)
- [Script Hub](https://hub.windmill.dev/)
- [GitHub Repository](https://github.com/windmill-labs/windmill)
- [Discord Community](https://discord.gg/windmill)
- [API Reference](https://www.windmill.dev/docs/api)

---

*This skill provides production-ready patterns for Windmill workflow automation, tested across enterprise scenarios with Python, TypeScript, Go, and Bash scripts.*

## Sub-Skills

- [1. Python Scripts](1-python-scripts/SKILL.md)
- [2. TypeScript/Deno Scripts](2-typescriptdeno-scripts/SKILL.md)
- [3. Go Scripts](3-go-scripts/SKILL.md)
- [4. Bash Scripts](4-bash-scripts/SKILL.md)
- [5. Flow Orchestration](5-flow-orchestration/SKILL.md)
- [6. Schedule Management](6-schedule-management/SKILL.md)
- [7. Approval Flows](7-approval-flows/SKILL.md)
- [8. Resource and Secrets Management](8-resource-and-secrets-management/SKILL.md)
- [Integration with Database and Slack](integration-with-database-and-slack/SKILL.md)
- [1. Script Organization (+3)](1-script-organization/SKILL.md)
- [Common Issues (+1)](common-issues/SKILL.md)
