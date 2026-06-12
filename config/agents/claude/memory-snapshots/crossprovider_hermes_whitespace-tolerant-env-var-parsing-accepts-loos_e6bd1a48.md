---
name: crossprovider hermes whitespace-tolerant-env-var-parsing-accepts-loos
description: Whitespace-tolerant env var parsing accepts loose truthy values
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [bash-parsing, safety-gates, whitespace-handling]
---

Awk-based key matching without trim (`$1 == key`) allows keys with leading spaces, enabling quoted/padded truthy values to slip through strict rejection logic. Normalize key names and implement strict boolean checks; test both `GATEWAY_ALLOW_ALL_USERS = "yes"` (spaces before key) and `"yes"` (padded value) as negative cases.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
