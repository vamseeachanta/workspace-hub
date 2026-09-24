---
name: crossprovider codex cli-help-surface-is-more-authoritative-than-impl
description: CLI help surface is more authoritative than implementation code
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-correctness, cli, contracts, verification]
---

When CLI command help and implementation function signatures diverge, the CLI is the real user contract. A function may accept arguments that the `--help` doesn't expose, or vice versa. Verify the CLI surface (`--help`, subcommands) before trusting code documentation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
