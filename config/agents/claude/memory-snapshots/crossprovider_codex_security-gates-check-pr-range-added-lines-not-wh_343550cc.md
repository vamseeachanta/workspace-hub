---
name: crossprovider codex security-gates-check-pr-range-added-lines-not-wh
description: Security gates check PR-range added lines, not whole tree
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [security-gates, pr-scope, deny-lists, code-review]
---

Deny-list scans on added lines in PR diff range are practical security gates (catches new leaks). Full-repo scans are noisy (catch pre-existing violations outside the PR scope) and slow. Use PR-range scope for batch gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
