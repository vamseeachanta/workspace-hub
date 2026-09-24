---
name: crossprovider gemini frozen-dataclasses-for-tabular-domain-objects-wi
description: Frozen dataclasses for tabular domain objects with dual representation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [domain-modeling, dataclass, immutability]
---

Use @dataclass(frozen=True) for domain models (CasingString, ProductionTimeSeries) to enforce immutability. Provide both tabular (CSV/matrix) and visual (SVG/HTML) representations. This enables clean data transformation pipelines and multiple output formats from a single in-memory representation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
