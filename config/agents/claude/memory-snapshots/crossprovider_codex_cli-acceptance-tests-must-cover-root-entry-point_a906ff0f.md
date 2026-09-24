---
name: crossprovider codex cli-acceptance-tests-must-cover-root-entry-point
description: CLI acceptance tests must cover root entry point, not just subcommands
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, cli, acceptance-criteria]
---

Testing a focused subcommand app (e.g., a Typer subapp) doesn't prove root CLI dispatch works when modules use eager imports at initialization. Acceptance criteria claiming root-command success must explicitly invoke the root entry point or console script, not just the subcommand.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
