---
name: repo-structure-allowed-in-docs
description: 'Sub-skill of repo-structure: Allowed in docs/ (+1).'
version: 1.4.0
category: workspace
type: reference
scripts_exempt: true
---

# Allowed in docs/ (+1)

## Allowed in docs/


| Content Type | Location |
|-------------|----------|
| Reference docs — explains how a module works | `docs/modules/<domain>/` or `docs/domains/<domain>/` |
| How-to guides for humans | `docs/guides/` |
| API documentation | `docs/api/` |
| Data source descriptions | `docs/data-sources/` |
| Migration guides | `docs/guides/migration-*.md` |
| Domain-specific references | `docs/<domain>/` (e.g., `docs/hse/`, `docs/petrophysics/`) |


## NOT Allowed in docs/


| Misplaced File | Correct Location |
|----------------|-----------------|
| `AGENT_OS_COMMANDS.md` | DELETE (agent_os is archived) |
| `MANDATORY_SLASH_COMMAND_ECOSYSTEM.md` | `.claude/docs/` or DELETE |
| `AI_AGENT_ORCHESTRATION.md` | `.claude/docs/ai-orchestration.md` |
| `AI_USAGE_GUIDELINES.md` | `.claude/docs/` if agent-facing, else `docs/guides/` |
| `sub_ai/` directory | `.claude/docs/` |
| `raw_data/` | `data/<domain>/` |
| `prompt-review/` | `.claude/docs/` or delete |
| WRK deliverable reports | `workspace-hub/.claude/work-queue/done/` |
| Session notes | `.claude/docs/` or delete |

**Rule**: If a file in `docs/` contains slash commands, agent protocols, or provider instructions, it belongs in `.claude/docs/`, not `docs/`.

---
