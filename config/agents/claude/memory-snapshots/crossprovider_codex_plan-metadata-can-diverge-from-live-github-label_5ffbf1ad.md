---
name: crossprovider codex plan-metadata-can-diverge-from-live-github-label
description: Plan metadata can diverge from live GitHub labels
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-approval, github-coordination, metadata-sync]
---

Local `.planning/plan-approved/NNN.md` frontmatter can show `status:plan-review` while the live GitHub issue is labeled `status:plan-approved`. Check both; the live issue label is the coordination source of truth. Stale plan frontmatter should be treated as a documentation lag, not ground truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
