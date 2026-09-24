---
name: crossprovider codex untracked-implementation-creates-false-passes-in
description: Untracked implementation creates false passes in staged-enforcement gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement, git-state, testing]
---

Enforcement gates that scan `--all-tracked` or `--staged` modes create false passes when implementation files remain untracked, hiding a failure path that emerges on commit. This is a git-mode hazard specific to tools like legal/deny-list scanners. Verification must separately test that untracked implementation will pass once tracked, not just trust current-state gate success.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
