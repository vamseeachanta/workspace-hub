---
name: crossprovider codex installation-presence-vs-repo-artifact-presence-
description: Installation presence vs repo artifact presence are distinct runtime states
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [temporal-coupling, installation-state, provider-detection]
---

Repo-tracked files (config/agents/*/AGENTS.runtime.md, SOUL.runtime.md) prove a contract exists, not that a provider is installed on a machine. Provider presence must check actual runtime paths (~/.codex, ~/.hermes) or CLI availability, not static repo files. Collapsing these creates false PARITY verdicts on boxes with stale provider installation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
