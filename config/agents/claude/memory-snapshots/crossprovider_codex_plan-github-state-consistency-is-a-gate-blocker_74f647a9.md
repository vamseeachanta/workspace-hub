---
name: crossprovider codex plan-github-state-consistency-is-a-gate-blocker
description: Plan/GitHub state consistency is a gate blocker
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [gate-review, github-state, consistency]
---

Plans must align across frontmatter status, README rows, live GitHub labels, and file existence (e.g., `.planning/plan-approved/NNN.md`). Mismatches (status=draft locally but status:plan-approved on GitHub, or missing approval marker files) signal approval-state drift and break downstream work.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
