---
name: crossprovider hermes skills-don-t-auto-persist-across-hermes-context-
description: Skills don't auto-persist across hermes context compression
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, skills, session-state, ux]
---

Hermes re-asks 'should I load skill X?' multiple times per session despite prior loads, because state doesn't survive compaction. Explicitly load required skills once at session start; do not assume prior-turn state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
