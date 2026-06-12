---
name: crossprovider hermes verification-first-closure-gate-before-implement
description: Verification-first closure gate before implementation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [execution, verification, early-gate, closure]
---

Before implementing any fix, explicitly pre-check whether the issue is already done: inspect deliverable surface, run targeted validators/tests, read issue/PR/commit evidence, and compare against acceptance criteria. Evidence for 'already done' must include direct proof in current repo state, verification artifact, linkage to commit/PR/file evidence, and acceptance-criteria coverage. This catches already-satisfied issues early and prevents wasted work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
