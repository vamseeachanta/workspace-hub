---
name: crossprovider hermes codex-sandbox-constraints-require-workarounds-pr
description: Codex sandbox constraints require workarounds; prefer Claude for batches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [provider-constraints, sandbox-issues, model-selection]
---

Codex 0.125.0 hits bwrap/loopback issues on some systems; use `--dangerously-bypass-approvals-and-sandbox` as workaround. For sustained batch work (planning, review, multi-lane orchestration), Claude is more reliable; route batch work to Claude when Codex sandbox stability is uncertain.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
