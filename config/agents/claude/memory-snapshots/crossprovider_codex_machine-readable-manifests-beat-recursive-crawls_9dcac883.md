---
name: crossprovider codex machine-readable-manifests-beat-recursive-crawls
description: Machine-readable manifests beat recursive crawls for large share inventories
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [large-scale-data, manifest-driven, scope-bounding]
---

For filesystem triage, use JSON manifests + targeted spot-checks instead of unbounded `find`/`du` scans. Interrupt long-running optional probes—they're not load-bearing for triage and consume time without bounded completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
