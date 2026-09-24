---
name: crossprovider codex pre-completion-cleanup-audit-must-run-read-only-
description: Pre-completion cleanup audit must run read-only to name residue state; prevents carrying governance debt
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, governance, closure]
---

Before finalizing any review, run the cleanup audit in report-only mode. Classify residue as CLEAN (proceed), EXPECTED (proceed with note), or UNEXPECTED (block). Skipping this step leaves behind orphaned worktrees, dirty state, and untracked files that cause downstream friction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
