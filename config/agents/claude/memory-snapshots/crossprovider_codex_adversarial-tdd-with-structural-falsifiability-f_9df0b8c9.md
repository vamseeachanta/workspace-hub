---
name: crossprovider codex adversarial-tdd-with-structural-falsifiability-f
description: Adversarial TDD with structural falsifiability for mutation/enforcement code
metadata:
  type: reference
  source: codex
  bridged: 2026-07-13
  tags: [tdd, infrastructure, verification, mutation-safety]
---

Infrastructure code that controls system state changes (schedulers, mutations, enforcement) requires RED→GREEN cycles with focused adversarial tests covering corner cases: executable-literal abuse, guard-ordering bypasses, sentinel parsing evasion. Verify full suite + lint + legal + diff review before committing; staged-index testing ensures committed bytes match what's tested.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
