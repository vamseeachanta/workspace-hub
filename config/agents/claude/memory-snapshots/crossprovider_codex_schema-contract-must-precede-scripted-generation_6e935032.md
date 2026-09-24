---
name: crossprovider codex schema-contract-must-precede-scripted-generation
description: Schema contract must precede scripted generation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, metadata, code-generation]
---

For multi-step processes with scripted artifact generation, define metadata schema explicitly (keys, types, edge model, cardinality, normalization) BEFORE writing generators. Inverted sequence (schema after generation) breaks downstream steps and requires regeneration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
