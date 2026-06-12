---
name: crossprovider gemini catalog-consistency-tests-verify-actual-properti
description: Catalog consistency tests verify actual properties
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, pattern, catalog]
---

Catalog metadata tests check entries match actual file properties (hull dimensions, panel counts, mesh quality metrics). WRK-110/WRK-115/WRK-116 test that hull_panel_catalog.yaml dimensions match YAML profiles and GDF meshes; WRK-113 verifies source-registry matches actual update frequencies. Catches silent catalog-data divergence.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
