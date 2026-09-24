---
name: crossprovider codex generated-artifact-validation-is-orthogonal-to-c
description: Generated artifact validation is orthogonal to code testing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifacts, generated-data, validation, testing]
---

Code can pass unit tests while generated JSON/JSONL outputs contain duplicates, stale data, or incorrect transformations. Example: post-dedupe candidate lists repeated identical source IDs; tests passed. Require direct artifact inspection (jq, schema validation, consistency checks) separate from code review; verify report invariants (counts match JSONL, no duplicate keys in dedupe pools) explicitly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
