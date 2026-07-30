---
name: crossprovider codex cli-testing-focused-app-tests-don-t-prove-root-d
description: CLI testing: focused-app tests don't prove root dispatch works
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [cli, testing, dispatch]
---

Testing a focused Typer sub-app can pass while the root CLI dispatch via entry point fails. Acceptance criteria requiring root command success must explicitly test the root app or console entry point, not just a sliced CLI subcommand.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
