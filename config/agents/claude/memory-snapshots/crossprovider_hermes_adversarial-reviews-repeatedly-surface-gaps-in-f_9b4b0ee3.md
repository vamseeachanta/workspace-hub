---
name: crossprovider hermes adversarial-reviews-repeatedly-surface-gaps-in-f
description: Adversarial reviews repeatedly surface gaps in failure-path test coverage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [adversarial-review, test-coverage, acceptance-gates]
---

Three independent reviews of the #2766 implementation found missing tests for malformed remote evidence, inaccessible paths, and schema mismatches—cases the happy-path tests never exercised. Each time a failure-path test was added, an earlier unhanded malformed-evidence case was exposed. Recommendation: before approval, ensure test matrix explicitly covers happy path, missing/malformed/null cases, and known error conditions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
