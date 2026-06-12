---
name: crossprovider codex awk-acceptable-for-frozen-yaml-schemas-yq-needed
description: awk acceptable for frozen YAML schemas, yq needed for schema evolution
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tooling, parsing]
---

Lightweight awk extraction works for small, stable YAML schemas (shallow keys, few optionals), but nested fields or schema expansion require a real parser (yq) to avoid brittle hacks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
