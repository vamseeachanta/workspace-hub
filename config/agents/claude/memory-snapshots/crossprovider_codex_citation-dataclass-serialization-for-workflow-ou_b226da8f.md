---
name: crossprovider codex citation-dataclass-serialization-for-workflow-ou
description: Citation dataclass serialization for workflow outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [serialization, citations, workflow-output]
---

Citation objects must be serialized with `asdict()` before placement in JSON-structured workflow results; raw dataclass instances cause output shape regressions and fail downstream consumers expecting dicts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
