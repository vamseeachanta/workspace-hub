---
name: crossprovider codex cross-provider-automation-needs-normalized-outpu
description: Cross-provider automation needs normalized output format
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [automation, multi-provider, parsing]
---

Tools invoking multiple external systems (LLMs, CLIs, APIs) must normalize each system's outputs to a canonical form BEFORE parsing. Provider-specific parsing per invocation introduces silent defects (format mismatches, missing fields, non-deterministic verdicts). A single adaptation layer is more maintainable and safer.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
