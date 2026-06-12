---
name: crossprovider hermes adversarial-test-suites-need-wrong-but-valid-loo
description: Adversarial test suites need 'wrong but valid-looking' inputs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, adversarial-qa, llm-wiki, hermes]
---

#77 tests used well-formed, consistent inputs and passed while implementation had symlink/consistency bugs. Adversarial test coverage requires handcrafted corrupt artifacts (mismatched CSV/JSON counts, forged evidence, symlinked sources outside repo, stale digests). Current test suite covering happy-path + malformed is insufficient for integrity/security gates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
