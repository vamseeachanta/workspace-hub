---
name: crossprovider codex scope-leak-detection-to-newly-generated-surfaces
description: Scope leak detection to newly generated surfaces, not whole pages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, testing, scope-boundary, privacy]
---

When verifying that generated sections do not leak sensitive data, scan only the git diff and newly generated sections, not entire page files. Whole-page scans false-fail on pre-existing inherited metadata in frontmatter/body that was already present before the generation step, masking real new leaks or incorrectly rejecting valid generated content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
