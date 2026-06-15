---
name: crossprovider codex broad-filesystem-searches-without-depth-limits-e
description: Broad filesystem searches without depth limits exceed useful runtime
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [performance, large-repos, search-patterns]
---

Large repos with generated data (e.g., llm-wiki): `find|rg` patterns without `-maxdepth` or `--max-depth` run to timeout/hang. Require explicit depth bounds and process termination; don't rely on timeouts to clean up. Particularly hazardous when combined with concurrent status probes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
