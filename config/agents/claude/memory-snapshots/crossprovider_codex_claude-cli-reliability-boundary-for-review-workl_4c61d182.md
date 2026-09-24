---
name: crossprovider codex claude-cli-reliability-boundary-for-review-workl
description: Claude CLI reliability boundary for review workloads
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [claude-cli, orchestration, reliability, gates, cross-review]
---

Claude interactive session (this session) can orchestrate the work pipeline; Claude CLI (claude -p) has payload-size boundaries and cannot reliably serve as an automated gate reviewer. WRK-642 testing confirmed three failure categories (payload-size, positional-arg harness bug, process cleanup leak). Codex is the hard gate in cross-review.sh precisely because of this boundary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
