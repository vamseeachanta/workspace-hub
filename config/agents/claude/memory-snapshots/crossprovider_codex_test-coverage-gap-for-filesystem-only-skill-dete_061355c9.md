---
name: crossprovider codex test-coverage-gap-for-filesystem-only-skill-dete
description: Test coverage gap for filesystem-only skill detection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, skills-audit, filesystem-inventory]
---

`tests/skills/test_weekly_skills_audit.py` lacks coverage asserting that active filesystem-only `SKILL.md` files are detected and reported distinctly from tracked active skills. This gap corresponds to the missing feature in the audit script.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
