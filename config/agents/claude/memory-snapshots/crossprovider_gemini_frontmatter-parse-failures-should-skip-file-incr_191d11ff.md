---
name: crossprovider gemini frontmatter-parse-failures-should-skip-file-incr
description: Frontmatter parse failures should skip file + increment counter, not crash
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [error-handling, data-robustness, nightly-jobs]
---

Wrap frontmatter parsing in try/except; on ValueError/YAMLError, increment files_skipped_malformed and continue. Soft failures let nightly jobs proceed; l2_meta provenance reports the skips.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
