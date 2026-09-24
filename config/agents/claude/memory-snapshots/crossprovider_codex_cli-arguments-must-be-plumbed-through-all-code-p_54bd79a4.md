---
name: crossprovider codex cli-arguments-must-be-plumbed-through-all-code-p
description: CLI arguments must be plumbed through all code paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cli-design, testing-gaps, api-consistency]
---

When a CLI accepts a flag like `--contract`, verify it's actually used in every scanning mode (direct scan, review, snapshot, etc.) not just one path. Tests often cover only the primary flow and miss secondary modes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
