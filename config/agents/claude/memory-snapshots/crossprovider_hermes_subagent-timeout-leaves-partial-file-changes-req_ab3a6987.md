---
name: crossprovider hermes subagent-timeout-leaves-partial-file-changes-req
description: Subagent timeout leaves partial file changes requiring manual re-sync
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-dispatch, subagent-limits, ci-repair, operational-risk]
---

Parallel subagents dispatched to repair CI/test suites across repos hit 600s timeout, landing partial file changes (e.g., formatting in worldenergydata, tests in digitalmodel). Subsequent manual discovery and re-application required; strategy is tighter timeout windows, non-overlapping work partition, or sequential dispatch for interdependent tasks.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
