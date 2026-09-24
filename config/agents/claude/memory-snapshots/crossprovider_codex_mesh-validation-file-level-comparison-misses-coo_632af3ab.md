---
name: crossprovider codex mesh-validation-file-level-comparison-misses-coo
description: Mesh validation: file-level comparison misses coordinate changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [mesh-validation, testing-methodology, CFD, correctness]
---

Raw file digest or hash comparison does not prove mesh motion or coordinate integrity; comparing outputs requires parsing coordinate payloads and comparing numerically or using explicit reconstruction of parallel output trees before comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
