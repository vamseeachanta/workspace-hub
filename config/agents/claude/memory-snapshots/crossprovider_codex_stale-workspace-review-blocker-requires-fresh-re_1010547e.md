---
name: crossprovider codex stale-workspace-review-blocker-requires-fresh-re
description: Stale workspace review blocker requires fresh re-run or explicit user waiver
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [review-process, governance, cross-provider]
---

Plan reviews against outdated workspace snapshots (e.g., Gemini testing on 2026-04-29 state when plan was revised 2026-04-30) produce false-positive MAJOR findings (404 / archived-repo claims). Require fresh cross-provider re-run or explicit user waiver; single-author review cannot distinguish stale-snapshot MAJOR from genuine blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
