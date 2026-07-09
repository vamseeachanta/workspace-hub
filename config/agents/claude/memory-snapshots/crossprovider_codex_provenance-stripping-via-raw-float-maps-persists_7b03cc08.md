---
name: crossprovider codex provenance-stripping-via-raw-float-maps-persists
description: Provenance-stripping via raw-float maps persists even after wrapping in dataclasses
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [data-quality, provenance, antipattern, conversion-factors]
---

Conversion factors stored as `dict[str, float]` lose source citation metadata. Wrapping in a dataclass does not fix this if the public interface exposes the map directly; tests and parser boundaries must enforce that every float value is derived from a source-attributed factor object, not a raw value.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
