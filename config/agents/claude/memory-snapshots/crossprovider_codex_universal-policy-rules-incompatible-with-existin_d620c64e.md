---
name: crossprovider codex universal-policy-rules-incompatible-with-existin
description: Universal policy rules incompatible with existing corpus shape
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [policy, corpus-shape, WRK-1053, skill-library]
---

WRK-1053 proposes README.md required in all skill directories. Repo has 508 SKILL.md files but only 32 README.md files; enforcing presence would flag ~500 'violations' and be immediately non-actionable. Policy rules must account for corpus shape, or acceptance criteria must explicitly call for repo-wide migration first.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
