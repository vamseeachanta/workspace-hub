---
name: workstations
description: >
  Machine registry for multi-workstation workspace-hub usage. Tracks computer nicknames,
  OS, capabilities, and active work assignments. Reference when creating WRK items
  or planning which machine to use for specific tasks.
version: 1.0.0
updated: 2026-02-19
category: workspace-hub
triggers:
  - which computer
  - computer nickname
  - machine registry
  - working machine
  - multi-machine
  - computer field
related_skills:
  - workspace-hub/session-start
  - workspace-hub/work
capabilities:
  - machine-registry
  - computer-routing
requires: []
---
# Computers Skill — Machine Registry

Tracks workspace-hub machines for multi-computer workflows. The `computer:` field
in WRK items references a nickname from this registry.

## Machine Registry

> Nicknames TBD — update this section once settled.

| Nickname | OS | Primary Use | Notes |
|----------|-----|-------------|-------|
| (TBD) | Linux | — | — |
| (TBD) | Windows | — | — |

## WRK Item Integration

The `computer:` field is added to WRK frontmatter at **Capture** and confirmed
at **Plan** stage:

```yaml
computer: nickname   # machine where this work is intended to run
```

### When to set computer:

- Set at creation if the task is clearly machine-specific (e.g., requires local GPU,
  Windows tool, specific data drive)
- Leave blank if the task is machine-agnostic (hub-only docs, skills, queue management)
- Always set for `working/` items to enable multi-machine handoff tracking

### Multi-machine handoff

When switching machines, `/session-start` checks recent `working/` items for `computer:`
fields and prompts if the current machine differs from the last active one.

## Update Process

When adding a new machine:
1. Add a row to the registry table above
2. Update the `## Machine Registry` section with OS, primary use, notes
3. Commit: `chore(computers): add machine <nickname> to registry`
