---
name: crossprovider codex output-shape-regressions-from-non-serializable-o
description: Output shape regressions from non-serializable objects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [output-design, serialization, architecture, correctness]
---

Adding non-dict/list/scalar objects (Citation, custom classes) to results that might be JSON/YAML serialized breaks downstream workflows. Default output to plain dicts, or verify all output writers explicitly handle the type before introducing non-serializable fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
