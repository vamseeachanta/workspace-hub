---
name: crossprovider codex feature-flags-are-necessary-but-insufficient-for
description: Feature flags are necessary but insufficient for CLI commands
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [cli-tooling, command-registration, codex]
---

Enabling a CLI feature flag (e.g., `features.goals = true`) does not automatically expose the command. Commands require both the feature flag AND explicit registration (command files or agent/workflow entries) for the CLI to discover and display them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
