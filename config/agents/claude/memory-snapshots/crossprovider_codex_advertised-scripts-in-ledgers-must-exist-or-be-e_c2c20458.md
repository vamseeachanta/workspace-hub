---
name: crossprovider codex advertised-scripts-in-ledgers-must-exist-or-be-e
description: Advertised scripts in ledgers must exist or be explicitly marked as TBD
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ledger-maintenance, validation-gates, plan-accuracy, script-tracking]
---

Coordination ledgers and validation gates that reference scripts (e.g., `scripts/validate_*.py`) must point to existing repository files or explicitly mark them as placeholder/future work. Untracked references confuse readers and fail pre-commit audits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
