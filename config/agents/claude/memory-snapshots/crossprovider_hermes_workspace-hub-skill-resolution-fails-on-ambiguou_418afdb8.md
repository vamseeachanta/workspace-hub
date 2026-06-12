---
name: crossprovider hermes workspace-hub-skill-resolution-fails-on-ambiguou
description: Workspace-hub skill resolution fails on ambiguous names across local/external dirs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [workspace-hub, skill-loading, path-resolution]
---

`skill_view` fails when the same skill name exists in both `.claude/skills/` and `~/.claude/plugins/cache/` (external skill dirs); relative paths work but absolute paths are unsupported. Hermes cannot disambiguate without explicit path hints.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
