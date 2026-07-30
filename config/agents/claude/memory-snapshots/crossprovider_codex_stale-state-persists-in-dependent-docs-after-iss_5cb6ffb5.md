---
name: crossprovider codex stale-state-persists-in-dependent-docs-after-iss
description: Stale state persists in dependent docs after issue closure
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [issue-closure, documentation, state-drift]
---

When closing issues that unblock gates (e.g., #65/#69 implementing legal scans), update all referencing docs (README, coordination ledgers, other plans) that may still say 'X is unavailable.' State drifts across multiple files; closing the gate issue alone leaves old text behind.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
