---
name: crossprovider codex optional-feature-tests-must-cover-mixed-behavior
description: Optional-feature tests must cover mixed behavior boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, optional-features, worldenergydata]
---

Tests for optional features (e.g., `allow_default_density=True`) must exercise mixed behavior—some fields using registry factors while others default—not just uniform all-default or all-converted scenarios. Live/sidecar tests often miss this critical boundary and should cover both defaulted and converted fields in the same audit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
