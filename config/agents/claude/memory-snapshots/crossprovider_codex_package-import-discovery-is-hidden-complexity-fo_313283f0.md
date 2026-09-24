---
name: crossprovider codex package-import-discovery-is-hidden-complexity-fo
description: Package import/discovery is hidden complexity for doc tools
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [documentation, dependencies, tool-config]
---

For mkdocstrings, Sphinx, or similar API doc generators, the primary risk is usually import resolution: optional extras, namespace packages, editable install mode, optional runtime deps. Explicitly specify the docs environment model upfront rather than deferring.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
