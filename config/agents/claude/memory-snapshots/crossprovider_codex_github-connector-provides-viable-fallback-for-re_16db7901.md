---
name: crossprovider codex github-connector-provides-viable-fallback-for-re
description: GitHub connector provides viable fallback for reads when shell access is unavailable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [fallback-patterns, github-connector, resilience]
---

When shell wrapper fails (e.g., `bwrap: loopback: Failed RTM_NEWADDR`), GitHub read-connector can still retrieve live issue context, comments, file content, and repo state without local shell execution. This allows analytical phases (resource intel gathering, evidence verification) to proceed even when local writes/shell commands are blocked. Tested on issues #2449, #2452, #2450, #2438.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
