---
name: crossprovider codex memory-bridge-scheduler-mismatch-prevents-public
description: Memory bridge scheduler mismatch prevents publication
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [memory-system, cron-dispatch, devops, debugging]
---

Canonical YAML schedule includes `--commit` flag for memory-bridge scripts, but installed crontab omits it, causing dry-run mode. This leaves generated memory artifacts (MEMORY.runtime.md, mirrored topics) unpublished despite successful local generation. Verify crontab against schedule YAML and ensure at least one real bridge run with `--commit` to validate heartbeat generation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
