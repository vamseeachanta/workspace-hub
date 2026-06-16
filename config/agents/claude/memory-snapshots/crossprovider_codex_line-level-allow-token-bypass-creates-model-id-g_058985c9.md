---
name: crossprovider codex line-level-allow-token-bypass-creates-model-id-g
description: Line-level allow-token bypass creates model-ID guard false negatives
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [security-guard, false-negatives, allow-token-bypass, hardcoded-tokens]
---

Security guards that check allow-tokens at the line level skip entire lines if the token appears anywhere (e.g., `# latest_models` in a comment), allowing hardcoded model IDs on the same line to pass. workspace-hub PR #3070 issue #3060: `check-model-id-sourcing.sh` skips token comparison for lines containing `latest_models` or `registry_model(` anywhere. Minimal repro: `model = latest_models.get("anthropic", "claude-opus-4-9")` passes despite the hardcoded ID. Use token-specific or position-aware matching instead of line-level bypass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
