---
name: crossprovider codex policy-bypass-via-string-literals-in-gate-eviden
description: Policy bypass via string literals in gate evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, policy-bypass, validator-design, gate-authority]
---

Validators that accept hardcoded string literals (e.g., `durable_output_gate_evidence == "issue_61_verified"`) as proof of gate compliance are forgeable. Gate evidence must be anchored to actual resource references or external validation results, not user-supplied strings. Found in #52 wave-1 validator accepting synthetic `"issue_61_verified"` without actual #61 proof link.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
