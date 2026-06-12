---
name: crossprovider hermes cli-output-contract-tests-must-invoke-entrypoint
description: CLI output-contract tests must invoke entrypoint, not functions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, cli-design, acceptance-testing]
---

Unit tests calling render_html() directly miss CLI argparse, --format handling, exit codes, and unsupported modes. For tools with multiple output formats (JSON/Markdown/HTML), acceptance tests must invoke the script via subprocess, not call render functions directly. Weak assertions (substring presence) miss structural regressions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
