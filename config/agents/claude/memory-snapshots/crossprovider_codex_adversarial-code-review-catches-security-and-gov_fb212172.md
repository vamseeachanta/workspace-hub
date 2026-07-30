---
name: crossprovider codex adversarial-code-review-catches-security-and-gov
description: Adversarial code review catches security and governance defects that static analysis misses
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [review, security, governance, verification]
---

Multiple sessions uncovered: security hazards (opening device files with O_RDONLY blocks indefinitely before fstat() can reject), governance bypass (owner_decision_required flags that pass --check silently), unvalidated gates (enum/predicate checks trusted as booleans), and scope collisions (adjacent issues with blurred ownership). The pattern: assume defects, verify every claim against actual source and tests, cite file:line, never praise or restate, bias toward non-approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
