---
name: crossprovider codex manifest-and-artifact-schemas-must-be-formally-s
description: Manifest and artifact schemas must be formally specified before validation acceptance tests
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-design, acceptance-criteria, testing]
---

Plan #605 requires validation and replacement of `orcawave_package_manifest.json` but never defines schema version, integrity checks, or corruption handling. TDD lists have no corrupt-manifest, stale-manifest, or path-traversal cases. Plans can't validate manifest behavior without a formal schema contract; defer acceptance until schema is defined or remove validation from scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
