---
name: crossprovider codex issue-specific-selector-hardcoding-delays-genera
description: Issue-specific selector hardcoding delays generalization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, scanner-design, technical-debt]
---

The #68 public-surface scanner is hard-pinned to issue 68 (scripts/ace_public_surface_review.py:127, :152). New consumers like #63 must use explicit-path scanning or wait for #72 generalization. This creates workarounds and couples downstream work to #72 completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
