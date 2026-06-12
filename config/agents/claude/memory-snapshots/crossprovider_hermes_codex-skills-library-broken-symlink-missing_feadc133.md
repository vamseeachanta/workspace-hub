---
name: crossprovider hermes codex-skills-library-broken-symlink-missing
description: Codex skills library broken — symlink missing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tooling-bug, codex, skills, integration]
---

.codex/skills/ is a real directory containing only 57/2863 skills instead of a symlink to ../.claude/skills. Codex is missing 98% of available skills. Fix: rm -rf .codex/skills && ln -s ../.claude/skills .codex/skills

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
