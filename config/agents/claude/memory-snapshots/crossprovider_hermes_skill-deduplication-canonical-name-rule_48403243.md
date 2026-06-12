---
name: crossprovider hermes skill-deduplication-canonical-name-rule
description: Skill deduplication canonical-name rule
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills, taxonomy, deduplication]
---

In skill taxonomy, frontmatter 'name' field is canonical; leaf directory name is secondary. Duplicate detection must prioritize frontmatter-name matches to avoid false positives when names and paths diverge.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
