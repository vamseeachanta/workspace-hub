---
name: crossprovider codex adversarial-plan-review-checks-paths-consumers-c
description: Adversarial plan review checks: paths, consumers, contracts, determinism, toolchain
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [code-review, adversarial-review, planning, rigor]
---

Plans fail predictably in five dimensions: wrong file paths (verify with git ls-tree/grep), omitted consumers (exhaustive call-site search, not just obvious ones), contradictions between stated contract and implementation, determinism/atomicity asserted without tests, and violations of repository execution policy (e.g., bare python vs. uv run). Each is cheap to fix at plan stage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
