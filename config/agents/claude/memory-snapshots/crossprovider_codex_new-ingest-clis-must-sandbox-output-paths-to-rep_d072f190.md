---
name: crossprovider codex new-ingest-clis-must-sandbox-output-paths-to-rep
description: New ingest CLIs must sandbox output paths to repo directories
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [llm-wiki, input-validation, private-corpus]
---

Unrestricted `--output-path` and `--ledger` arguments in private-ingest tools can write arbitrary files or expose private paths. Enforce repo-local sandboxes (`data/document-index/`, `docs/reports/`) and validate all paths repo-local at the CLI layer, like adjacent code does.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
