---
name: crossprovider codex hermes-sibling-repo-skills-require-explicit-allo
description: Hermes sibling repo skills require explicit allowlist
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hermes, sibling-repos, skills-config]
---

Hermes default skill paths should resolve to central workspace-hub only (__WS_HUB_PATH__/.claude/skills); sibling repo provider adapters (e.g., __TIER1_REPO_ROOT__/digitalmodel/.claude/skills) need explicit per-repo allowlist in config, not automatic discovery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
