---
name: crossprovider codex unverified-api-and-schema-claims-in-plan-tasks
description: Unverified API and schema claims in plan tasks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-verification, schema-validation, plan-rigor]
---

Plans frequently assert that certain APIs exist, dataclass fields are present, or methods accept specific arguments, without verifying these claims against the actual codebase. Before writing a plan task that depends on an API, read the relevant source code and confirm the API exists and matches the claimed signature.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
