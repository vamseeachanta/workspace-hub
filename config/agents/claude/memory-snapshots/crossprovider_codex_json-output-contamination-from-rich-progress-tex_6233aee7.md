---
name: crossprovider codex json-output-contamination-from-rich-progress-tex
description: JSON output contamination from Rich/progress text breaks parsing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [cli, json, output-validation, formatting]
---

Rich formatting and progress output appended after JSON objects causes `JSONDecodeError: Extra data`. When implementing CLI that outputs JSON, validate strictly: emit ONLY parseable JSON for machine consumption (no progress text), and separate any human-facing output into stderr or structured envelopes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
