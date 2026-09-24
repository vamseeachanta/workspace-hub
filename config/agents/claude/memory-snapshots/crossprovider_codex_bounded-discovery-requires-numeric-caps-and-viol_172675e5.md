---
name: crossprovider codex bounded-discovery-requires-numeric-caps-and-viol
description: Bounded discovery requires numeric caps and violation tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [filesystem-safety, test-coverage, privacy-control]
---

Stating 'bounded discovery' or 'max-depth limits' without numeric depth, file-count, timeout bounds and tests that fail on violations allows implementations to bypass controls via unbounded os.walk, symlink traversal, or manifest searches. Caps must be explicit integers with tests that assert traversal depth, entry counts, and short-circuits are enforced.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
