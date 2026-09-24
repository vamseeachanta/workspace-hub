---
name: crossprovider codex cli-output-format-flags-must-apply-uniformly-acr
description: CLI output format flags must apply uniformly across all formats
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [CLI-design, command-interface, defect-pattern]
---

Commands supporting multiple output formats (JSON/table/CSV) should apply filtering/display flags uniformly or explicitly reject them; silent discarding of filter effects in non-JSON formats is a usability defect.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
