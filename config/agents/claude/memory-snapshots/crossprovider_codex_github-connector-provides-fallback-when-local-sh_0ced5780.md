---
name: crossprovider codex github-connector-provides-fallback-when-local-sh
description: GitHub connector provides fallback when local shell fails
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-api, sandbox, resilience]
---

Sandbox network failures (bwrap loopback issues) can block all local shell commands. GitHub connector surfaces can inspect public repo artifacts, issue history, and visibility metadata as a read-only fallback.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
