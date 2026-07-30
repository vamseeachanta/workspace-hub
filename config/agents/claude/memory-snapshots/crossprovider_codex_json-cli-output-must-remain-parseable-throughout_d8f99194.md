---
name: crossprovider codex json-cli-output-must-remain-parseable-throughout
description: JSON CLI output must remain parseable throughout
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cli, json, output-format]
---

No progress spinners, Rich formatting, or text appended after JSON object. Every sub-command's output form must match its advertised format; contamination breaks JSON consumers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
