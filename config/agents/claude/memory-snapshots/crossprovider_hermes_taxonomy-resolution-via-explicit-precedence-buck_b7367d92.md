---
name: crossprovider hermes taxonomy-resolution-via-explicit-precedence-buck
description: Taxonomy resolution via explicit precedence bucketing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [taxonomy-design, classification-policy, review-resilience]
---

When ambiguous reference types resist classification (e.g., stale references, non-repo artifacts), resolve by defining an explicit precedence order (blank → symbolic → external → sibling_repo → non_repo_artifact → repo) and bucketing each item with clear allowed/protected/deferred designations. Vague categories fail review.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
