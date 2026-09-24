---
name: crossprovider gemini commit-hook-enforcement-wrk-nnn-required-for-fea
description: Commit hook enforcement: WRK-NNN required for feat/fix/refactor, flexible for chore/docs
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, git-hooks, work-tracking]
---

check-commit-msg.sh blocks feat/fix/refactor commits without WRK-NNN reference; chore warns if >3 files; docs/test/merge/style/ci are exempt. This balances work tracking (functional changes) with flexibility for minor changes. Hook logic could be more robust (target first line explicitly rather than grep).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
