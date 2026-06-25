---
name: crossprovider codex staged-blob-inspection-catches-leaks-when-whole-
description: Staged-blob inspection catches leaks when whole-file scans would fail
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [privacy-review, staged-inspection, diff-scoping]
---

When reviewing privacy-sensitive changes where generated sections are appended to pages that already contain historical sensitive data, scanning whole files or unified diffs will false-positive. Use `git show :path` to read staged blobs directly, then scan only added lines, generated sections, and new files. Diff-scoped and added-line-scoped regex are tools; full page scans defeat the point.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
