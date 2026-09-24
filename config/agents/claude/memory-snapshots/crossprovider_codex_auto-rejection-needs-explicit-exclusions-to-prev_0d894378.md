---
name: crossprovider codex auto-rejection-needs-explicit-exclusions-to-prev
description: Auto-rejection needs explicit exclusions to prevent false positives
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-safety, auto-classification, false-positive-risk]
---

Content-pattern-based auto-rejection (ISBN/ICS/copyright + no numeric data, or empty amendment forms) must explicitly exclude edge cases: single-column content tables (may be valid) and blank CSVs (may be failed extractions). Without exclusions, legitimate tables are silently retired to terminal parse_status=rejected.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
