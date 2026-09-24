---
name: crossprovider codex consume-from-canonical-data-sources-don-t-rederi
description: Consume from canonical data sources, don't rederive
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-architecture, single-source-of-truth, coupling]
---

When a system has an authoritative data source (taxonomy, manifest, registry), read from it directly rather than hard-coding derived values. Rederivation diverges over time and defeats the purpose of maintaining a canonical source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
