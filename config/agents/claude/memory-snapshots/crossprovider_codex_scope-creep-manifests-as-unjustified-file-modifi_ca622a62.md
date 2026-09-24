---
name: crossprovider codex scope-creep-manifests-as-unjustified-file-modifi
description: Scope creep manifests as unjustified file modifications in Files-to-Change
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, scope, review]
---

Plans add files like `.claude/skills/...` or config files to modifications without explaining why they're in scope. Each entry in Files-to-Change needs a reason-for-change sentence; lack of one signals scope drift. Spot-check during review: does this file's modification advance the stated issue deliverable or is it a follow-on?

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
