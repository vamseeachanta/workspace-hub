---
name: crossprovider codex documentation-edits-alone-do-not-enforce-runtime
description: Documentation edits alone do not enforce runtime behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, work-queue, acceptance-criteria]
---

Plans that change only SKILL.md or procedural docs fail to satisfy acceptance criteria requiring runtime action (e.g., 'Phase 1 calls detect-drift.sh'). Executable changes to scripts, hooks, config, or the Python analysis layer must accompany documentation changes. Diagnosing whether SKILL.md is procedural guidance vs. a hard hook is critical.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
