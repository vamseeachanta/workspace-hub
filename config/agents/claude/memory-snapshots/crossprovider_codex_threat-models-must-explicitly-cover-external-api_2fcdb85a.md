---
name: crossprovider codex threat-models-must-explicitly-cover-external-api
description: Threat models must explicitly cover external APIs, secrets, path traversal, and CLI tool dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [threat-model, security, plan-review, dependencies]
---

Threat models regularly omit: external API security and data leakage (especially to third-party embeddings/LLM services), symlink traversal for path allowlists, repository-root trust assumptions, and CLI tool/utility availability. For scripts using external APIs, secrets, or filesystem ops, these are blocking gaps, not optional depth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
