---
name: crossprovider codex private-denied-literals-in-test-fixtures-must-co
description: Private/denied literals in test fixtures must convert before self-scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [public-scan-safety, negative-fixtures, self-reference-hazard]
---

When a test file contains negative examples (source IDs, private paths, denied commands), plan explicit conversion to runtime-built or allowlisted equivalents before committing. Self-scanning requirements expose such cases late; 47 denied errors in a test file is a blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
