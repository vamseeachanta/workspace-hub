---
name: crossprovider hermes tdd-for-file-artifacts-requires-schema-validatio
description: TDD for file artifacts requires schema validation, not just existence checks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [tdd, testing, artifact-validation]
---

When the deliverable IS the file (YAML, config, manifest, JSON), tests that only verify file existence silently pass malformed or semantically wrong content. Always parse and validate against expected structure or schema; file-exists-only tests are too weak for artifact-centric TDD.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
