---
name: crossprovider hermes ace-linux-2-remote-execution-has-higher-failure-
description: ace-linux-2 remote execution has higher failure rate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-machine, execution-reliability]
---

ace-linux-2 overflow lanes fail more frequently (Codex auth issues, Gemini capacity limits). Keep ace-linux-1 as the control plane for decisions/GitHub mutations; use ace-linux-2 for overflow execution only after local success.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
