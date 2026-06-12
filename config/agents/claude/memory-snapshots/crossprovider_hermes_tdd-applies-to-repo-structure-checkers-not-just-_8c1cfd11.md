---
name: crossprovider hermes tdd-applies-to-repo-structure-checkers-not-just-
description: TDD applies to repo-structure checkers, not just feature code
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [repo-structure, testing, process]
---

Checker scripts and validation tools are part of the codebase and follow TDD discipline: write failing test first, verify RED, then implement GREEN. Checker bugs can silently pass files that should be rejected.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
