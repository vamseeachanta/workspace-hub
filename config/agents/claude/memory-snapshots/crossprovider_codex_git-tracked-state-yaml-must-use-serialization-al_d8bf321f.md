---
name: crossprovider codex git-tracked-state-yaml-must-use-serialization-al
description: Git-tracked state YAML must use serialization allowlist
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-tracked-state, serialization, secrets-prevention]
---

Machine-state files must never serialize command lines, absolute paths, environment variables, auth tokens, or cron/dispatch content; only typed enums, booleans, counts, and approved repo labels are safe.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
