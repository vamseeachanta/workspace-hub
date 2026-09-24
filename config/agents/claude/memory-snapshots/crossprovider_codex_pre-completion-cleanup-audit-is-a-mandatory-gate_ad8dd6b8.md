---
name: crossprovider codex pre-completion-cleanup-audit-is-a-mandatory-gate
description: Pre-completion cleanup audit is a mandatory gate before handoff
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, cleanup, governance]
---

Run `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md` before claiming task complete; audit surfaces residue as CLEAN/EXPECTED/UNEXPECTED. Never report completion with UNEXPECTED residue present.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
