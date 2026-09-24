---
name: crossprovider codex workspace-hub-ssot-pattern-sibling-repos-symlink
description: Workspace-hub SSoT pattern: sibling repos symlink to canonical skills
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workspace-hub, architecture, symlink-pattern]
---

In the workspace-hub ecosystem, `.claude/skills` lives once at `workspace-hub/.claude/skills` and is consumed by sibling repos via symlinks to `../workspace-hub/.claude/skills`. Machine roots and repo layout are resolved from `config/workstations/registry.yaml`; the resolver filters to repos that exist and contain SKILL.md. Removes hardcoded nested paths. Applied in #2775 SSoT restoration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
