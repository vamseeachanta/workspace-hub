---
name: crossprovider codex coordination-ledger-diverges-from-live-github-st
description: Coordination ledger diverges from live GitHub state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [coordination, state-sync, hazard]
---

Local tracking files (docs/plans/README.md, coordination YAML) record stale draft/approval snapshots that no longer match live GitHub labels (#61, #63, #72 are status:plan-review upstream but tracked as draft locally). Audits must verify against live `gh issue view` output before trusting cached blocker states.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
