---
name: crossprovider codex ci-commands-must-be-verified-against-written-spe
description: CI commands must be verified against written specifications line-by-line
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [CI, contracts, governance]
---

Audit CI command arguments, flags, and tool choices against documented requirements; even semantically-weaker variants (e.g., using #68 public-surface scanner instead of #63 canary) will pass the 'did it run' gate. Specification mismatch is a defect requiring explicit re-audit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
