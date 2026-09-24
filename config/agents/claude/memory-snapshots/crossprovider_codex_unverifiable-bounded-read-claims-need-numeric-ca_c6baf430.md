---
name: crossprovider codex unverifiable-bounded-read-claims-need-numeric-ca
description: Unverifiable bounded-read claims need numeric caps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, scope, security, testing]
---

Assertions that a dataset read is 'bounded' or 'limited' without explicit max_bytes, max_rows, or max_files are unverifiable and frequently violated. Large datasets require precomputed sidecars or header-only metadata. Write tests that fail if full-manifest operations are used, not just assumed to be out of scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
