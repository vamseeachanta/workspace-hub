---
name: crossprovider codex shell-wrapper-for-universal-cli-defaults-despite
description: Shell wrapper for universal CLI defaults despite project-level overrides
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, cli-configuration, multi-repo-patterns]
---

When project-level tool config can override user defaults, inject CLI flags via shell wrapper (highest precedence) to enforce consistent behavior across all repositories. Pattern: set global config + add wrapper script that injects the critical flag. Verified across 102+ Git checkouts that this ensures the flag applies everywhere despite project-level config.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
