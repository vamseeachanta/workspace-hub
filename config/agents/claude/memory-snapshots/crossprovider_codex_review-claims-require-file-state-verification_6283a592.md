---
name: crossprovider codex review-claims-require-file-state-verification
description: Review claims require file-state verification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [review-process, verification, acceptance-criteria]
---

When a review asserts 'feature is fixed', 'tests committed', or 'script updated', verify against git status and actual file content in the review environment before accepting. Review text can lag implementation; untracked files, stale code, and mismatched artifact claims can hide for multiple rounds. WRK-1053 had claims of 8/8 passing tests and UV_CACHE_DIR exports that did not match actual repo state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
