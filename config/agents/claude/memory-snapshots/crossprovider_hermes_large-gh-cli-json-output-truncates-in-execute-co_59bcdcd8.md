---
name: crossprovider hermes large-gh-cli-json-output-truncates-in-execute-co
description: Large gh CLI JSON output truncates in execute_code — workaround: save to file first
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gh-cli, execute-code, json]
---

gh issue list --json returns ~82KB for 194 issues; execute_code caps terminal output at ~50KB, truncating JSON silently. Workaround: save to file via terminal (no cap), then read/process. Affects gh searches with >50 results and --json output.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
