---
name: crossprovider codex recorded-commands-for-reproducibility-must-inclu
description: Recorded commands for reproducibility must include all required CLI flags
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [reproducibility, command-recording, audit]
---

Storing a validator command as `uv run python script.py --emit-evidence <ref>` in evidence loses context when the CLI actually requires `--share-root` and `--reviewed-commit`. When that stored command is later replayed for audit, it fails silently or returns wrong output. Solution: store the full command with all required flags and environment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
