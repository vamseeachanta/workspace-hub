---
name: crossprovider codex verification-then-operate-windows-are-a-vulnerab
description: Verification-then-operate windows are a vulnerability class
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, initialization, verification-timing, bootstrap]
---

When code verifies a resource early but performs mutations later (commit, push, visibility changes), the interval enables interception or substitution. Attestation must immediately precede the operation it covers, not earlier in the workflow. Reproducible across bootstrap, initialization, and factory patterns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
