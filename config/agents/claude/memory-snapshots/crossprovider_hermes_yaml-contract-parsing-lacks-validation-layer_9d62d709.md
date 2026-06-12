---
name: crossprovider hermes yaml-contract-parsing-lacks-validation-layer
description: YAML contract parsing lacks validation layer
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [yaml, validation, error-handling]
---

Repo-structure checkers load contract YAML (allowed_roots, generated_artifact_roots, etc.) without type/schema validation. Malformed YAML causes uncaught exceptions (e.g., invalid frozenset type) instead of graceful error. Add schema validation or catch before contract use.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
