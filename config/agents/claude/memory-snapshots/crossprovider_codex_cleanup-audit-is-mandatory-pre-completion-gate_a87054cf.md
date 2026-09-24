---
name: crossprovider codex cleanup-audit-is-mandatory-pre-completion-gate
description: Cleanup audit is mandatory pre-completion gate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cleanup-audit, pre-completion-gate, mandatory]
---

Before claiming task complete, run `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`. Surface residue in three buckets: CLEAN / EXPECTED (proceed with named residue) / UNEXPECTED (block completion). Must report this audit result explicitly; never claim completion with UNEXPECTED residue present.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
