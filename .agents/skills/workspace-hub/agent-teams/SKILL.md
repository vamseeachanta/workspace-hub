---
name: agent-teams
description: "Agent team protocols for workspace-hub \u2014 when to use teams, decision\
  \ matrix, team lifecycle, communication patterns, and MAX_TEAMMATES=3 constraint"
version: 1.0.0
category: workspace-hub
author: workspace-hub
type: skill
last_updated: 2026-03-10
wrk_ref: WRK-212
related_skills:
- orchestrator-routing
- improve
- repo-sync
tags:
- agent-teams
- orchestration
- protocols
- coordination
- parallel-agents
platforms:
- all
capabilities: []
requires: []
---

# Agent Teams

## Sub-Skills

- [Core Constraint](core-constraint/SKILL.md)
- [Workspace Work Profile (Updated 2026-03-10)](workspace-work-profile-updated-2026-03-10/SKILL.md)
- [Activation](activation/SKILL.md)
- [Decision Matrix: Team vs Sequential](decision-matrix-team-vs-sequential/SKILL.md)
- [1. Create team (+5)](1-create-team/SKILL.md)
- [DM (default — always prefer) (+2)](dm-default-always-prefer/SKILL.md)
- [Agent Types for Common Tasks](agent-types-for-common-tasks/SKILL.md)
- [Work Queue Integration](work-queue-integration/SKILL.md)
- [Subagent startup convention (+2)](subagent-startup-convention/SKILL.md)
- [Idle State](idle-state/SKILL.md)
- [Related](related/SKILL.md)

## Iron Law

> No task shall spawn more than 3 concurrent subagents (MAX_TEAMMATES=3) — no matter how parallelizable the work appears.

## Rationalization Defense

| Excuse | Reality |
|--------|---------|
| "This task has 5 independent parts — 5 agents would be faster" | More agents means more coordination overhead, more context conflicts, and more merge failures. The limit is empirically derived. |
| "I'll just use 4 this one time" | The limit exists because every team that exceeded 3 hit coordination failures. There is no safe "just one more." |
| "These agents don't need to coordinate" | Even "independent" agents contend for git locks, file writes, and context. Zero-coordination is a myth in a shared repo. |

## Red Flags

These phrases signal you are about to violate the Iron Law:
- "we could parallelize this into N agents" (where N > 3)
- "one more agent won't hurt"
- "these are fully independent — no coordination needed"
- "the limit is conservative for this case"
