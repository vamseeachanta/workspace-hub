---
name: crossprovider codex format-changes-to-state-files-require-auditing-a
description: Format changes to state files require auditing all consumers
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [state-format, backward-compat, consumer-audit]
---

Changing `active-wrk` from single WRK ID to two-line record (WRK ID + started_at) breaks any script reading that file without updating. State format changes need exhaustive consumer audit or a single reader/writer interface to prevent silent breakage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
