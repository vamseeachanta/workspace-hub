---
name: crossprovider codex cross-agent-script-reliability-requires-explicit
description: Cross-agent script reliability requires explicit exit-code handling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [orchestration, shell-reliability, cross-agent]
---

`scripts/review/submit-to-codex.sh` reports failures as success (exit 0) in several branches, breaking caller detection. Agents invoking review scripts need deterministic non-zero exit codes on failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
