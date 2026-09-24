---
name: crossprovider codex catalog-and-on-disk-state-diverge-significantly-
description: Catalog and on-disk state diverge significantly at corpus scale
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-inventory, catalog-management, scale-readiness]
---

When building multi-publisher standards catalogs, cataloged doc counts routinely lag on-disk reality by 2× or more; orphaned dirs appear on-disk but not in metadata. Before scaling ingests (e.g., ASTM), regenerate the catalog deterministically from on-disk tree with sorted traversal, validation checks (per-dir counts vs filesystem), and atomic publish.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
