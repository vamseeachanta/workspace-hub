---
name: crossprovider codex line-level-exemption-tokens-create-false-negativ
description: Line-level exemption tokens create false negatives when appearing in comments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [enforcement-scripts, false-negatives, security-gaps]
---

Allow-tokens that exempt entire lines (like `latest_models`, `registry_model(`) create false negatives when the token appears anywhere on the line—including in comments or variable names. A line like `fallback = "claude-opus-4-9" # latest_models` incorrectly passes validation. Use structured, per-line sentinels instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
