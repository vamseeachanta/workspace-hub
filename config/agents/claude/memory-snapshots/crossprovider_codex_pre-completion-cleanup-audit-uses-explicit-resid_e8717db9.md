---
name: crossprovider codex pre-completion-cleanup-audit-uses-explicit-resid
description: Pre-completion cleanup audit uses explicit residue classification to prevent silent debt accumulation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup, residue-management, completion-gates, session-hygiene]
---

Classify task residue as CLEAN (ready to exit) / EXPECTED (known unrelated state, safe to preserve) / UNEXPECTED (blocks completion until resolved). This three-bucket model prevents silent accumulation of orphan stashes, locked worktrees, or unmerged conflicts that force later heavyweight remediation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
