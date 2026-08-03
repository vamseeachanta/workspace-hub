---
name: crossprovider codex latest-view-external-apis-vulnerable-to-revision
description: Latest-view external APIs vulnerable to revision races
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [concurrency, external-apis, gotcha]
---

APIs that return latest state (e.g., datasets-server) are vulnerable to races between verification steps. Use immutable commit hashes and verify consistency before and after each API call to prevent time-of-check-to-time-of-use gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
