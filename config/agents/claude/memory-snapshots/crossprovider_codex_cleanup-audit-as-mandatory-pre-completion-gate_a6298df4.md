---
name: crossprovider codex cleanup-audit-as-mandatory-pre-completion-gate
description: Cleanup audit as mandatory pre-completion gate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [completion-gate, session-hygiene]
---

Before declaring work complete, run the cleanup audit from `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`. Surface residue as CLEAN, EXPECTED, or UNEXPECTED. Never report completion with UNEXPECTED residue present—resolve it first or block closure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
