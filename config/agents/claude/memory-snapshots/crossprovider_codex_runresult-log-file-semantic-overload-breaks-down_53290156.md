---
name: crossprovider codex runresult-log-file-semantic-overload-breaks-down
description: RunResult.log_file semantic overload breaks downstream contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [design-flaw, result-envelope, backwards-compatibility]
---

When OrcaWave API backend assigns `.owr` binary results to `log_file` field, it breaks the contract for consumers expecting a text log path. Subprocess backend assigns text log path to the same field. Downstream code interprets field differently by backend. Needs refactor to separate `log_file` and `results_file` paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
