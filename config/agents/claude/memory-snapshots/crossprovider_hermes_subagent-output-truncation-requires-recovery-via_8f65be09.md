---
name: crossprovider hermes subagent-output-truncation-requires-recovery-via
description: Subagent output truncation requires recovery via temp files or Python parsing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [subagent-output, truncation, recovery]
---

Subagent task results and large terminal tool outputs can be truncated in summary. Capture full output to temp files (`/tmp/...`), read them back with `Read` tool, or use Python subprocess to recover complete results before processing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
