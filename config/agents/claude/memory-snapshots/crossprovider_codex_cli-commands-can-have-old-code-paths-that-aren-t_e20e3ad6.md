---
name: crossprovider codex cli-commands-can-have-old-code-paths-that-aren-t
description: CLI commands can have old code paths that aren't wired to new functionality — new features exist but unreachable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [command-wiring, feature-exposure, cli-stale-path]
---

New classifiers or routes may be implemented but the CLI command still invokes an old code path. `ace_classification_from_inventory` exists but `main()` returns only `classify_inventory`. Verify that new features are actually exposed through user-facing CLI surfaces.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
