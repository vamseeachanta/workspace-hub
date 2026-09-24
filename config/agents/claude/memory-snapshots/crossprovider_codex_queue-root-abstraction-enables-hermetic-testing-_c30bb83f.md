---
name: crossprovider codex queue-root-abstraction-enables-hermetic-testing-
description: Queue-root abstraction enables hermetic testing of directory-structured data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, testability, cli-design]
---

Scripts operating on structured data directories should accept configurable root paths via environment variables or CLI flags (e.g., `WORK_QUEUE_ROOT`, `--queue-root`) with sensible defaults. This enables hermetic tests using `mktemp -d` fixtures without file copying or live-queue pollution, and supports multiple queue instances in production.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
