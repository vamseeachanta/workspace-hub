---
name: crossprovider hermes pydantic-models-text-generation-patterns-for-cod
description: Pydantic models + text-generation patterns for code synthesis
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [code-generation, pydantic]
---

ANSYS/fatigue/CP modules use Pydantic dataclasses for config (with realistic offshore defaults) + generate text command strings (APDL, YAML) via string formatting, NOT file I/O. No subprocess calls to external tools—pure Python string building. Generator methods return multi-line command text ready for file write.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
