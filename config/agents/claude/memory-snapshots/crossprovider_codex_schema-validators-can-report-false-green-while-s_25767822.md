---
name: crossprovider codex schema-validators-can-report-false-green-while-s
description: Schema validators can report false green while schemas are never invoked
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, schema, security, audit]
---

Validators performing only collection/anchor checks can print '0 findings' and pass gates while never calling jsonschema.validate(). Distinguish between ad-hoc collection logic and formal schema enforcement when reviewing validation code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
