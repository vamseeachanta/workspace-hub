---
name: crossprovider gemini silent-stderr-suppression-masks-pipeline-failure
description: Silent stderr suppression masks pipeline failures
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [scripting, error-handling, debugging]
---

Using `2>/dev/null` on steps that can fail (like python3 render) hides the root cause and leads to wasted retries. Log or fail fast instead; silence only post-validation, non-critical steps.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
