---
name: crossprovider codex plan-validation-specificity-is-a-review-gate
description: Plan validation specificity is a review gate
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, review-gates, validation]
---

Plans that promise validation (external links, query surface, domain routing) must include executable commands (pytest, curl, concrete assertions) or named fallbacks. Vague 'will be validated' language triggers REQUEST_CHANGES from reviewers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
