---
name: crossprovider gemini vessel-fleet-module-as-centralization-target
description: Vessel fleet module as centralization target
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [architecture-decision, worldenergydata, data-centralization]
---

When legacy and new rig fleet systems coexist (BSEE WAR-derived vs vessel_fleet module), expand the newer system rather than refactoring legacy; newer module has richer schema (50+ fields), operator configs, and dedup/quality infrastructure built-in. Avoid digging into legacy unless strictly necessary.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
