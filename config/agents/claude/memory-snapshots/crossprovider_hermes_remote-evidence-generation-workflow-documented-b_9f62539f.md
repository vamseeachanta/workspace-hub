---
name: crossprovider hermes remote-evidence-generation-workflow-documented-b
description: Remote evidence generation workflow documented but not implemented
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, readiness, evidence-generation, workflow]
---

Docs specify `scripts/readiness/telegram-hermes-readiness.sh --host <id> --evidence-dir <dir>` generates host-local evidence JSON, but shell wrapper only execs Python CLI and Python only reads `--evidence-dir`, never writes `<host_id>.json`. Prescribed remote recovery path cannot produce required artifact; no end-to-end test covers the workflow.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
