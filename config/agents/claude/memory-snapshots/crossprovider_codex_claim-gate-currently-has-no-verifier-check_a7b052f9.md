---
name: crossprovider codex claim-gate-currently-has-no-verifier-check
description: Claim gate currently has no verifier check
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, claim-gate, metadata, verification-gaps]
---

Claim gate verification is entirely absent from verify-gate-evidence.py. WRK-677 proposes adding it with checks for session_owner, quota_snapshot (ISO8601 timestamp + pct_remaining), and blocking_state. New fields must be extracted by claim-item.sh.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
