---
name: crossprovider codex structured-output-review-transport-needs-bounded
description: Structured-output review transport needs bounded isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [review-transport, process-isolation, validation-gaps]
---

Claude and Gemini non-interactive review requires: bounded execution in isolated temp dir, deterministic input assembly, strict schema validation, and durable artifact capture before normalization. Current wrappers have incomplete cleanup (process-group leaks on timeout) and type-coercion false-positives (invalid JSON renders as VALID).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
