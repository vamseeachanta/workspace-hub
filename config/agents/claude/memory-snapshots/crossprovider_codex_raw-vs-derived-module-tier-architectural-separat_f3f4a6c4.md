---
name: crossprovider codex raw-vs-derived-module-tier-architectural-separat
description: Raw-vs-derived module-tier architectural separation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, separation-of-concerns, layering]
---

Separate raw-schema/ingestion/methodology layers from derived-analytics/views layers into distinct modules. Allows derived layers to evolve independently and prevents breaking raw ingestion contracts when analytics change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
