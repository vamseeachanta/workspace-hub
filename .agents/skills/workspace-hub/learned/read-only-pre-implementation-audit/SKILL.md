---
name: read-only-pre-implementation-audit
description: Systematic cross-check workflow to validate assumptions before TDD coding begins
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["tdd", "audit", "pre-coding", "read-only", "assumptions"]
---

# Read-Only Pre-Implementation Audit

Before coding Night 1, perform a structured read-only audit: sample large files (JSONL, logs) rather than reading full; trace test expectations against production script behavior; check for format mismatches (single-line JSONL vs. pretty-printed); identify missing stubs that tests wrap with `|| true`; verify env var handling is already production-ready. Document confirmed behavior, blockers, and exact files that must change. This prevents TDD implementation from breaking on hidden format or dependency mismatches.