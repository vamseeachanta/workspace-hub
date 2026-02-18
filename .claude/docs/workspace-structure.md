# Workspace Hub — Canonical Directory Structure

> **Established**: 2026-02-18 (WRK-200)
> **Status**: Active — this supersedes all prior structure diagrams and agent-os docs

## Canonical Layout

```
workspace-hub/                   ← hub root (git repo with submodules)
  .claude/                       ← ALL Claude-specific config (CANONICAL)
    commands/                    ← slash commands (hub-authoritative)
      agents/, analysis/, automation/, data/, github/, sparc/
      today.md, truth/, verify/, workflows/, work.md, workspace-hub/
    docs/                        ← internal process docs (this file)
    hooks/                       ← Claude lifecycle hooks
    rules/                       ← coding/git/legal rules
    skills/                      ← CANONICAL skill source (hub)
      engineering/               ← domain engineering skills
        drilling/, financial-analysis/, oil-and-gas/
        marine-offshore/, cad/, structural/, fatigue/
      data/, ai/, science/, operations/, workspace-hub/
    work-queue/                  ← work items (hub-central)
      pending/, working/, archived/, blocked/
  .codex/                        ← Codex provider config
    skills → ../.claude/skills   ← SYMLINK to hub skills
  .gemini/                       ← Gemini provider config
    skills → ../.claude/skills   ← SYMLINK to hub skills
  config/                        ← project config
    agents/                      ← model-registry.yaml, behavior-contract.yaml
    ai-tools/                    ← subscriptions, usage tracking
  coordination/                  ← Python library: Pydantic schemas for hub YAML
                                    (work_queue.py, reflect_state.py, learnings.py)
  docs/                          ← human-readable documentation
    modules/                     ← domain docs (ai/, automation/, workflow/)
  monitoring-dashboard/          ← Express/TypeScript+React monitoring app (tracked)
  reports/                       ← generated reports (timestamped)
  scripts/                       ← ALL automation scripts
    agents/                      ← work queue pipeline + lib/
    coordination/routing/        ← provider routing + lib/
    improve/                     ← session improvement + lib/
    operations/compliance/       ← legal scan, spec validation
    maintenance/                 ← model audit, ecosystem propagation
  specs/                         ← formal specs
    wrk/WRK-NNN/                ← per-item execution specs (Route C)
    repos/<repo>/                ← repo-specific domain specs
    templates/                   ← spec templates
  data/                          ← datasets (raw/, processed/, results/)
  logs/                          ← runtime logs (gitignored)
  <repo-submodules>/             ← all submodule repos (lowercase-kebab)
```

## Per-Submodule Layout

```
each-repo/
  .claude/
    CLAUDE.md                    ← adapter (generated from hub AGENTS.md)
    commands/                    ← subset of hub commands (propagated)
      agents/, analysis/, automation/, github/, sparc/
      today.md, truth/, verify/, workflows/, work.md
    skills/                      ← repo-local skills (if any)
    settings.json                ← repo-specific Claude settings
  .codex/                        ← Codex adapter
    skills → ../../.claude/skills  ← SYMLINK to hub skills
  .gemini/                       ← Gemini adapter
    skills → ../../.claude/skills  ← SYMLINK to hub skills
  src/                           ← source code
  tests/                         ← all tests
  docs/                          ← repo-specific docs
  scripts/                       ← repo-specific scripts only
  data/                          ← repo input data
  reports/                       ← generated output (gitignored)
```

## What Was Removed (WRK-200, 2026-02-18)

| Removed | From | Replaced By |
|---------|------|-------------|
| `.claude-flow/`, `.hive-mind/`, `.swarm/` | all repos | Gitignored everywhere |
| `modules/` (root) | workspace-hub | `scripts/automation/`, `config/agents/` |
| `skills/` (root) | workspace-hub | `.claude/skills/` |
| `ruv-swarm/`, `flow-nexus/` (root) | workspace-hub | Deleted (were hook propagations) |
| `hive-mind/`, `flow-nexus/`, `pair/`, `stream-chain/` etc. | `.claude/commands/` in submodules | Hub command propagation |
| `agents/domain/` (3 agent-os agents) | worldenergydata | `.claude/skills/engineering/` SKILL.md |

## What Was Kept (Intentional, Not Orphans)

| Directory | Repo | Purpose |
|-----------|------|---------|
| `coordination/` | workspace-hub root | Python library: Pydantic YAML schemas |
| `monitoring-dashboard/` | workspace-hub root | Express+React monitoring app |
| `docs/modules/` | workspace-hub | Domain docs (AI, automation, workflow) |
| `agent-library/` | `.claude/` | Loaded by `standard-development.yaml` + 4 devops skills — HIGH RISK to rename |

## Invariants (Must Not Change Without WRK Item)

1. `.claude/skills/` at hub root — canonical skill source
2. `.codex/skills` → `../.claude/skills` (hub), `../../.claude/skills` (submodules)
3. `.gemini/skills` → same as above
4. `config/agents/model-registry.yaml` — single source of truth for model IDs
5. `.claude/work-queue/` — referenced by hooks and session scripts
6. `scripts/agents/lib/` — negated in gitignore (`!scripts/agents/lib/`)
7. `scripts/coordination/routing/lib/` — negated in gitignore
8. `scripts/improve/lib/` — negated in gitignore

## Skills Ecosystem Health Check

Run: `.claude/hooks/ecosystem-health-check.sh`

As of 2026-02-18: **437 active skills, 30 archived**
