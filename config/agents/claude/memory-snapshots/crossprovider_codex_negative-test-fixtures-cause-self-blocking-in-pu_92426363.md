---
name: crossprovider codex negative-test-fixtures-cause-self-blocking-in-pu
description: Negative test fixtures cause self-blocking in public repos
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [testing, ci, public-repos, fixtures]
---

Committing negative test examples to public repos (especially in CI-scanned directories) causes the repository's own validators to reject the repo. Generate negative cases at runtime or temp-file scope instead. This is especially risky when parent scanners perform breadth-first scans of committed artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
