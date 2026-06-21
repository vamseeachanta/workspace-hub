---
name: crossprovider codex cli-boundary-guards-don-t-protect-programmatic-r
description: CLI boundary guards don't protect programmatic reuse — builder functions need independent path validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [path-safety, api-design, security-boundary]
---

When a builder function accepts output paths directly (not validated at call site), an intermediate API layer or library consumer can bypass the CLI guard. Output path validation must live in the builder itself, not just at the `main()` boundary. See: conference_canary_scaleout_followthrough.py accepts json_report_path and html_report_path without _validate_output(), only main() applies it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
