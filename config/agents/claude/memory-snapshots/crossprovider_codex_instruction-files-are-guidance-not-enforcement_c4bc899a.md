---
name: crossprovider codex instruction-files-are-guidance-not-enforcement
description: Instruction files are guidance, not enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, gates, contracts, fail-closed]
---

Plans claiming to enforce a contract via instruction updates (CODEX.md, CLAUDE.md, etc.) often lack the actual enforcement mechanism. Real enforcement requires fail-closed code that exits non-zero on contract violation, tested explicitly. Instruction files set expectations but can be skipped.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
