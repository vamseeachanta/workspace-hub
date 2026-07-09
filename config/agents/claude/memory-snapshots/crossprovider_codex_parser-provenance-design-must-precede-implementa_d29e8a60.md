---
name: crossprovider codex parser-provenance-design-must-precede-implementa
description: Parser provenance design must precede implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [data-provenance, parser-design]
---

When a parser applies conversion factors (e.g., tonnes→bbl), design upfront how used/defaulted/missing factors are captured in provenance metadata and how that metadata flows to downstream consumers (reports, adapters). Postponing this creates brittle handoffs where data lineage is lost.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
