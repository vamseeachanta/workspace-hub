---
name: crossprovider hermes uv-run-python3-c-inline-script-timeout-with-larg
description: uv run python3 -c inline script timeout with large payloads
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [uv-isolation, data-processing, workspace-hub]
---

When parsing large orchestrator logs (73K+ records) via `uv run python3 -c "..."` inline, the command times out after ~60s and returns empty output. Workaround: write the script to `/tmp/` file first, then run `uv run python /tmp/script.py` instead. This respects workspace-hub's uv isolation rules while avoiding the inline payload limit.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
