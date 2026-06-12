---
name: crossprovider hermes skill-commit-requires-read-only-coherence-verifi
description: Skill commit requires read-only coherence verification gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills, QA, workflow]
---

Before committing changes to workflow-coordination skills (issue-planning-mode, github-issues), run a read-only verification pass to ensure changes maintain coherence across related workflow definitions. This prevents silent contradictions between coordination patterns.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
