---
name: crossprovider hermes claude-code-plan-mode-permission-mode-plan-is-sa
description: Claude Code plan mode (--permission-mode plan) is safe for cloud audits; execution phase stays local
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-code, cloud-execution, architecture]
---

Claude Code v2.1.92+ supports --permission-mode plan (read-only, no writes). Can run headless via --print with USD budget cap. Suitable for Phase 1 (audit) + Phase 2 (planning) of refactors in cloud. Phase 3 (code changes) requires interactive sessions with full permissions—user-in-loop gate needed. Feasible for batching architecture audits across tier-1 repos.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
