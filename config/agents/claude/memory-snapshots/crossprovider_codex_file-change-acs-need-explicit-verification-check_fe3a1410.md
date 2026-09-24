---
name: crossprovider codex file-change-acs-need-explicit-verification-check
description: File-change ACs need explicit verification checks, not just inclusion in the file list
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, verification, process-artifacts]
---

Plans that require index updates (e.g., "Update docs/plans/README.md") must include a concrete verification command or test that the entry exists and is correct. Omitting the check leaves the AC discoverable-but-ignorable at implementation time, creating post-merge drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
