---
name: crossprovider codex large-repo-searches-need-early-stopping-heuristi
description: Large repo searches need early-stopping heuristics to avoid expansion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-quirk, large-repo, performance]
---

Broad `rg --files` and `git diff` operations in repos with large data/generated trees consume significant time and can expand unexpectedly into binary/cache artifacts. Narrow searches to specific file types or directories early; stop broad operations after a few seconds if hitting data trees, then use exact-path reads instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
