---
name: crossprovider codex non-blocking-enforcement-exit-0-is-ignored-at-sc
description: Non-blocking enforcement (exit 0) is ignored at scale; gates need hard stop behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, process, workflow]
---

In high-throughput workflows (40+ commits/day, multiple agents), WARN-mode pre-push hooks that exit 0 get normalized and ignored. Enforcement gates require either hard exit codes (reject the push) or visible downstream consequences (block PR merge, escalate to on-call). Default-allow enforcement does not change behavior in practice.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
