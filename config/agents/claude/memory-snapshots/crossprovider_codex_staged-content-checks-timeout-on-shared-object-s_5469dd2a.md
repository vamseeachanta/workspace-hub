---
name: crossprovider codex staged-content-checks-timeout-on-shared-object-s
description: Staged-content checks timeout on shared object stores
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [environment, git-performance]
---

In repositories with shared `.git/objects`, conflict-marker and legal-scan hooks on staged blobs can run silently for multiple minutes. This is not a deadlock; it is expected enforcement overhead. Plan for multi-minute commit times in such repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
