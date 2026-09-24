---
name: crossprovider codex dataclass-tuple-validation-in-json-chains-is-bli
description: Dataclass tuple validation in JSON chains is blind
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dataclass, json-serialization, validation-hazard]
---

Adding optional tuple fields to dataclasses used in JSON serialization (via `asdict` + downstream validators) can create validation holes: blind `tuple(...)` conversion accepts scalar strings as per-character iteration, bypassing container-type checks. Validators must check container type, not just element iteration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
