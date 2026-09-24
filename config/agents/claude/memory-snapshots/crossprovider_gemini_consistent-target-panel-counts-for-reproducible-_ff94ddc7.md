---
name: crossprovider gemini consistent-target-panel-counts-for-reproducible-
description: Consistent target panel counts for reproducible mesh generation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [mesh-generation, reproducibility, best-practice]
---

When generating hull panel meshes in batches (e.g., library expansions), enforce a single `TARGET_PANELS` constant (e.g., 2500) across all hull forms. This ensures consistent mesh density, predictable file sizes, and reproducible solver behavior across the library.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
