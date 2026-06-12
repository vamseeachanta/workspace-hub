---
name: crossprovider codex catalog-reproducibility-requires-exact-pinning-i
description: Catalog reproducibility requires exact pinning in install commands
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [reproducibility, version-pinning, catalog-design]
---

When storing reproducible install commands in YAML configs (e.g. mcp-servers.yaml), must use exact versions (PyPI ==, git SHA) not bare tool names (uvx mcp-server-fetch). Bare names fetch latest at install time, undoing the reproducibility claim and breaking the trust gate that pinning was meant to enforce.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
