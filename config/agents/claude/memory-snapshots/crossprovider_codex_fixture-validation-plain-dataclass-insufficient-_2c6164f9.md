---
name: crossprovider codex fixture-validation-plain-dataclass-insufficient-
description: Fixture validation: plain dataclass insufficient; require runtime coercion
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [config, validation, testing]
---

Configuration/fixture validation through plain dataclasses is unsafe. Must explicitly define JSON schema structure, enum/date conversion, unknown-key policy, field bounds, and deterministic validation errors. Absence of a validator means malformed config silently passes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
