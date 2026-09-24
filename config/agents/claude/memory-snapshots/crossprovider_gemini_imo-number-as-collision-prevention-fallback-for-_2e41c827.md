---
name: crossprovider gemini imo-number-as-collision-prevention-fallback-for-
description: IMO number as collision-prevention fallback for vessel hull_id in digital models
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [vessel-registry, maritime-data, schema-design]
---

When integrating external vessel records (e.g., worldenergydata) into naval architecture registries, consider IMO as a fallback or collision-prevention mechanism for hull_id. Commercial vessels use non-unique names but globally unique IMO identifiers, preventing ambiguity in digital model schemas that ingest fleet data.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
