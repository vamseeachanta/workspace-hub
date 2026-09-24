---
name: crossprovider codex generators-must-produce-validate-fail-closed-as-
description: Generators must produce+validate+fail-closed as a unit, with explicit operation guards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-generation, safety, validation]
---

Pattern: generator produces JSONL + JSON/HTML, validates schema and policy gates before write, rejects if source gates have drifted. Explicit operation guards (forbidding read_text, mkdir, write_text on non-repo paths) are required, not token-based filters. Fail-closed means invalid source state blocks output generation entirely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
