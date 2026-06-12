---
name: crossprovider hermes skill-tool-rejects-absolute-paths-workarounds-vi
description: Skill tool rejects absolute paths; workarounds via relative patterns only
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skill-loading, tool-constraints, workarounds]
---

`skill_view` tool constraint: only accepts relative skill names/patterns, rejects `/mnt/...` or `~/...` absolute paths. No tool-level workaround; resolution requires either (1) re-organizing skills to remove ambiguity, or (2) loading skill content via `read_file` after relative load succeeds.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
