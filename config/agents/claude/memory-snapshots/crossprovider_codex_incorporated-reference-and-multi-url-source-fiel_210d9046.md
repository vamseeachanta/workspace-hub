---
name: crossprovider codex incorporated-reference-and-multi-url-source-fiel
description: Incorporated-reference and multi-URL-source fields need precise data contracts to avoid intersection conflicts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-contract, field-definition, codex-finding]
---

When a plan introduces new fields like `incorporated-reference` that also need official URLs, the data contract must specify where jurisdiction/regulator evidence goes and how it intersects with existing URL allowlists. Underspecified fields create validation ambiguity and block implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
