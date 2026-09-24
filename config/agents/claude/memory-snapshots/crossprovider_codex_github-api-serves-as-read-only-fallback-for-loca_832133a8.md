---
name: crossprovider codex github-api-serves-as-read-only-fallback-for-loca
description: GitHub API serves as read-only fallback for local execution failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-api, fallback, multi-runtime]
---

When local shell execution is blocked (e.g., sandbox loopback failures), GitHub connector can still provide read-only data (branch diffs, file contents, branch metadata) sufficient for read-only reviews, enabling partial progress on inspection-only tasks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
