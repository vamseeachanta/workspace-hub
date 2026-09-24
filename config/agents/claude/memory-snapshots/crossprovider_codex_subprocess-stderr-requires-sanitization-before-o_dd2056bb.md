---
name: crossprovider codex subprocess-stderr-requires-sanitization-before-o
description: Subprocess stderr requires sanitization before output
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, logging, subprocess, cli]
---

CLI/subprocess stderr often contains private paths, API responses, or credentials even when the tool succeeds (HTTP 200, rc=0). Sanitize stderr before logging to reports/outputs. Tools like `gh`, `curl`, and cloud CLIs routinely leak context in stderr regardless of exit code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
