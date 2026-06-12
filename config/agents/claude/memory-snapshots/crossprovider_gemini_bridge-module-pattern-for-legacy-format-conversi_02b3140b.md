---
name: crossprovider gemini bridge-module-pattern-for-legacy-format-conversi
description: Bridge module pattern for legacy format conversion
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [data-migration, legacy-support, architecture]
---

Use bridge modules (e.g. rig_fleet_bridge.py) to convert curated vessel fleet → legacy BSEE format. RIG_NAME null fallback to VESSEL_NAME, pickle for internal-only data (nosec B301 justified). Implement 3-tier fallback (config > .local > committed) for data placement.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
