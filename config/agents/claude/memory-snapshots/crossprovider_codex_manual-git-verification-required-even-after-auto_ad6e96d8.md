---
name: crossprovider codex manual-git-verification-required-even-after-auto
description: Manual git verification required even after automated tense-audit; past-tense drift persists
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [past-tense-drift, verification-gap, manual-audit]
---

Automated tense-audits incompletely catch plans using past-tense language for future work. Reviewers must independently run `git show HEAD:<path>` or GitHub blob fetches to verify every 'created', 'added', or 'committed' artifact claim, because prose descriptions and automated checking frequently miss drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
