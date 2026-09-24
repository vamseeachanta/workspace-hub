---
name: crossprovider codex status-contradiction-blocks-closeout-local-ledge
description: Status contradiction blocks closeout (local ledger vs GitHub issue state)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, issue-tracking, coordination]
---

When local planning artifacts claim completion (`completed: true` in ledger) but GitHub issue shows `OPEN/status:plan-approved`, closeout is blocked. Local ledger must mirror GitHub state before declaring done. Verify with `gh issue view <N> --json state,labels`; reconcile before closing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
