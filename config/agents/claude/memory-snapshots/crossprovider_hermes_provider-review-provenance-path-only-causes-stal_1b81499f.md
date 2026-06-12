---
name: crossprovider hermes provider-review-provenance-path-only-causes-stal
description: Provider review provenance: path-only causes stale artifact review
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-workflow, provider-dispatch, artifact-staleness]
---

When running adversarial plan reviews via `plan-review-fanout.sh`, passing only the plan path causes reviewers to fetch stale GitHub `main` content instead of local-modified artifacts. Reviewers must include inline plan content or receive committed/pushed artifacts with explicit git SHA / working-tree markers. Path-only review is a silent provenance failure.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
