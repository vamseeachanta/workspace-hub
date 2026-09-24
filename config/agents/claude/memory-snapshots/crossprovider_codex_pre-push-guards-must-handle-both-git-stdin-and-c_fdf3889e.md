---
name: crossprovider codex pre-push-guards-must-handle-both-git-stdin-and-c
description: Pre-push guards must handle both Git stdin and Claude JSON hook formats
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hooks, git, claude, integration]
---

Pre-push guards receive native Git pre-push refs on stdin (space-separated lines) via `git push`, but Claude PreToolUse hooks send JSON. Guard must detect JSON format and infer push range from Git state; ignoring non-Git stdin prevents false negatives in CI/hook chains.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
