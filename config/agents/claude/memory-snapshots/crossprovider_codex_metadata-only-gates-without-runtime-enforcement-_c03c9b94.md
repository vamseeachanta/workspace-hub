---
name: crossprovider codex metadata-only-gates-without-runtime-enforcement-
description: Metadata-only gates without runtime enforcement are advisory only
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [gate-enforcement, configuration-contracts, metadata-vs-code]
---

YAML fields like `plan_mode: required` in stage contracts have no enforcement unless runtime code reads and verifies them. Annotations without consumer enforcement appear complete but are bypassed silently. Either add mechanical verification in stage runners or downgrade field names to mark them as advisory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
