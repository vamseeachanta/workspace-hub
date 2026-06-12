---
name: crossprovider hermes skill-path-ambiguity-in-dual-sourced-repo-extern
description: Skill path ambiguity in dual-sourced repo + external Hermes config
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-config, skill-loading, tool-constraints]
---

Hermes skill loader fails with 'ambiguous skill name' when skills exist in both `/home/vamsee/.hermes/skills/` and project-local `.claude/skills/`. `skill_view` rejects absolute paths (`/mnt/...`) with 'Non-relative patterns are unsupported', blocking workarounds. For dual-sourced repos, resolve ambiguity via explicit namespace prefix or prefer workspace-local skills in load order.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
