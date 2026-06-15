---
name: crossprovider codex distinguish-runtime-presence-from-repo-artifact-
description: Distinguish runtime presence from repo artifact presence
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [provider-detection, runtime-state, artifact-vs-installation]
---

Git-tracked config files (e.g., AGENTS.runtime.md) should not count as provider installation. A machine with no Codex CLI but with repo files will falsely report provider-present. True signals: CLI commands exist, symlinks point to live paths (e.g., ~/.codex/AGENTS.md), local runtime loads during initialization. Static repo text is evidence of contract, not operational state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
