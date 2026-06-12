---
name: crossprovider codex pandas-dtype-coercion-footguns-str-accessor-and-
description: Pandas dtype coercion footguns: `.str` accessor and `int()` cast on mixed object columns
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pandas-edge-cases, type-safety, data-pipelines]
---

Calling `.str.strip()` on object dtype columns containing non-strings converts them to NaN; calling `int(series.min())` on object-typed numeric strings raises AttributeError. Validate and coerce dtype before applying accessor methods.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
