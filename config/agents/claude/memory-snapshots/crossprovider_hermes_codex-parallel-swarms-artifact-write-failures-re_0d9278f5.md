---
name: crossprovider hermes codex-parallel-swarms-artifact-write-failures-re
description: Codex parallel swarms: artifact write failures recoverable via JSONL logs
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex, parallel-swarms, sandbox, recovery-pattern]
---

When multiple independent Codex `/goal` swarms fail to write artifacts locally (sandbox/permission constraints), findings are emitted in the final `turn.completed` message in JSONL logs. Extract via: `jq '.[] | select(.type=="turn.completed") | .content' logs/swarm-<n>-codex.jsonl`. Findings are not lost; only the file writes fail. Workaround applies to any parallel-agent write-failure scenario.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
