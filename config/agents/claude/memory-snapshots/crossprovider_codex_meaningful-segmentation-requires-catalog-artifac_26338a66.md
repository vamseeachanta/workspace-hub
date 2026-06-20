---
name: crossprovider codex meaningful-segmentation-requires-catalog-artifac
description: Meaningful segmentation requires catalog/artifact differentiation, not hardcoded aggregates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [data-architecture, segmentation]
---

Hardcoding one value per dimension (owned-project-family, mixed-discipline) from an aggregate is nominal, not meaningful. Real segmentation bucketes by catalog/folder/project so different artifacts produce different rows. Acceptance criteria requiring meaningful segmentation will fail nominal-only implementations in adversarial review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
