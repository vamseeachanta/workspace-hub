---
name: crossprovider codex untracked-public-artifacts-fail-legal-gate-regar
description: Untracked public artifacts fail legal gate regardless of content
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [legal, git-state, closure]
---

Retained implementation review artifacts must be staged/tracked before legal-sanity-scan --diff-only passes, even if content is scan-clean. Being untracked public-surface files causes intentional denial before validation runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
