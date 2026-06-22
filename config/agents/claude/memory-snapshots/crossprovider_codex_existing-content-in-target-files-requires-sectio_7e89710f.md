---
name: crossprovider codex existing-content-in-target-files-requires-sectio
description: Existing content in target files requires section-scoped leak tests, not full-page scans
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [testing, repo-state]
---

When a file already contains pre-existing content violating a compliance rule (e.g., existing dataset links), full-page leak tests will fail on pre-existing content. Use pre/post inventory assertions or git-diff scoping to test only newly-generated sections.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
