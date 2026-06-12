---
name: crossprovider hermes shared-repo-requires-preserving-pre-existing-dir
description: Shared repo requires preserving pre-existing dirty state across sessions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-agent, git-hygiene, shared-workspace]
---

Hermes agents run concurrently against workspace-hub; pre-existing untracked files (logs/, wiki reports, `.claude/state/`) must not be clobbered during cleanup/commit. Inventory before staging.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
