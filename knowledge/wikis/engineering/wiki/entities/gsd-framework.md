---
title: "GSD Framework"
tags: [workflow, gsd, planning, execution, phases]
sources:
  - working-style-memory
added: 2026-04-08
last_updated: 2026-04-08
---

# GSD Framework

"Get Stuff Done" -- the sole workflow framework for the workspace-hub ecosystem since 2026-03-25. Manages the full lifecycle: project initialization, phase planning, execution, verification, and shipping.

## Status: PRODUCTION (v1.34.1)

Requires Node.js 24+.

## Key Commands

| Command | Purpose |
|---------|---------|
| `/gsd:help` | Show available commands |
| `/gsd:progress` | Check project progress |
| `/gsd:new-project` | Initialize a new project |
| `/gsd:plan-phase` | Create detailed phase plan |
| `/gsd:execute-phase` | Execute all plans in a phase |
| `/gsd:verify-work` | Validate built features |
| `/gsd:ship` | Create PR, run review, prepare for merge |

## Workflow

```
discuss-phase -> plan-phase -> execute-phase -> verify-work -> ship
```

## Design Principles

- Tasks tracked as GitHub issues (no local ID systems)
- Plans, state, and research live in `.planning/` directory
- Atomic commits with deviation handling
- Wave-based parallelization for execution
- Checkpoint protocols and state management

## Cross-References

- **Related concept**: [[compound-engineering]]
- **Related concept**: [[orchestrator-worker-separation]]
- **Related entity**: [Skills System](../entities/skills-system.md)
