---
name: crossprovider codex hostile-negative-fixtures-must-not-be-committed-
description: Hostile negative fixtures must not be committed verbatim
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-scan, testing, legal-compliance, fixtures]
---

Negative examples (private field assignments, raw hashes, filesystem paths) should be assembled from fragments at runtime or generated dynamically, not stored as committed examples. Verbatim negative fixtures fail legal/security scans and create false negative test coverage. Parent test modules need conversion if they contain such examples.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
