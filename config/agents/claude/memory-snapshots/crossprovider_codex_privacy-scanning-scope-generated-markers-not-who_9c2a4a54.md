---
name: crossprovider codex privacy-scanning-scope-generated-markers-not-who
description: Privacy scanning scope: generated markers, not whole files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-review, methodology, scope-discipline]
---

Exact-label leak scans that check entire wiki files produce false positives from pre-existing page metadata outside generated blocks. Effective scanning requires bounding to generated-section markers (e.g., `dnv-extract-NNN:#issue`) unless the acceptance criterion explicitly changes to whole-file redaction. Separate checks for tracked vs. untracked artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
