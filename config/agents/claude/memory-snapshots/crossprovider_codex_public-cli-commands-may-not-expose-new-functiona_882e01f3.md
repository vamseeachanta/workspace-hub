---
name: crossprovider codex public-cli-commands-may-not-expose-new-functiona
description: Public CLI commands may not expose new functionality
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [cli-discoverability, user-surface, test-coverage]
---

New classifiers, helpers, or command variants can exist in the codebase (e.g., `ace_classification_from_inventory`) but not be wired to the public-facing command that users actually call (e.g., `classify` still only returns `classify_inventory`). Check that every new public-intended function has a CLI entry point and is covered in subprocess/integration tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
