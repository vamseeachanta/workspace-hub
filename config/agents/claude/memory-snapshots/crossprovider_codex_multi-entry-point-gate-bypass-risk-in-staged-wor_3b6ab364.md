---
name: crossprovider codex multi-entry-point-gate-bypass-risk-in-staged-wor
description: Multi-entry-point gate bypass risk in staged workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow-governance, gate-enforcement, multi-path-risk]
---

Gate enforcement must be implemented at all official workflow entrypoints (not just one canonical path), because agents can reach downstream stages through multiple paths: direct skill invocation, downstream validators, or out-of-band manual mutations. Classifying each path as official entrypoint vs. validator vs. manual mutation is required before implementation to ensure the fix covers all bypass routes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
