---
name: crossprovider codex path-leakage-in-argument-driven-generators
description: Path leakage in argument-driven generators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [path-safety, testing, generation, defect-class]
---

Generators accepting output path arguments can emit absolute paths into JSON artifacts even when internal safety gates pass; temp-path test fixtures using absolute paths do not detect leakage in generated output; set-based row identity checks do not reject duplicate target rows if the set is argument-derived. Test fixtures must validate argument handling, not just payload structure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
