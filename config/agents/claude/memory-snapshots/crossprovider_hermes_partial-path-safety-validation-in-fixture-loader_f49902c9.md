---
name: crossprovider hermes partial-path-safety-validation-in-fixture-loader
description: Partial path safety validation in fixture loaders
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [path-safety, fixture-validation, scope-containment]
---

Fixture loaders may validate some path fields (`required_citations`, `expected_paths`) but miss others (`corpus_surface`), creating escape routes for out-of-repo corpus references. Validate all path-bearing fields against repo boundaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
