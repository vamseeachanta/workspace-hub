---
name: crossprovider codex generated-wiki-artifacts-must-emit-all-frontmatt
description: Generated wiki artifacts must emit all frontmatter fields deterministically to pass artifact-parity tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [wiki-artifacts, schema, test-gate]
---

Schema-required fields like `tags`, `added`, `last_updated`, and `doc_key` must be emitted by the generator, not left as gaps. Missing fields break artifact-parity tests and violate the active frontmatter contract, even if existing pages have the same gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
