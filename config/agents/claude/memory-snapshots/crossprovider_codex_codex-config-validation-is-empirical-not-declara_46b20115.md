---
name: crossprovider codex codex-config-validation-is-empirical-not-declara
description: Codex config validation is empirical, not declarative
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [codex, config, tooling-quirk]
---

Official OpenAI docs reference keys like `tui.status_line`, but `codex --strict-config` does not validate them and no noninteractive mechanism exists to verify config structure. Empirically test against the installed CLI version before committing to config assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
