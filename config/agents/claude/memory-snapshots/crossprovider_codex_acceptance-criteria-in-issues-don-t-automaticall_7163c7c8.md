---
name: crossprovider codex acceptance-criteria-in-issues-don-t-automaticall
description: Acceptance criteria in issues don't automatically enforce in code
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [testing, verification, code-coverage, acceptance-criteria]
---

Quoted AC in GitHub issues require explicit code/test assertions to guarantee coverage; passing tests don't prove all quoted acceptance is met (found gap: AC 'broad traversal issues reference this gate' was not enforced in code or linked in matrix rows despite 24 passing tests).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
