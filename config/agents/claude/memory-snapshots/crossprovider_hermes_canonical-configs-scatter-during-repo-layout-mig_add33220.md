---
name: crossprovider hermes canonical-configs-scatter-during-repo-layout-mig
description: Canonical configs scatter during repo-layout migration; verify all in parallel
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [sibling-repos, config-drift, migration-checklist, hermes, codex-gemini]
---

Sibling repo migration broke Hermes external_dirs template, Codex/Gemini symlinks, and AGENTS.md pointers independently across three locations. Configuration isn't centralized; a migration verification must probe all config files that reference repo paths—fixing one doesn't guarantee others work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
