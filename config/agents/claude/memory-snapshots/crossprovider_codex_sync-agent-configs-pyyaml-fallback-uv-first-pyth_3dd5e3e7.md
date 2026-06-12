---
name: crossprovider codex sync-agent-configs-pyyaml-fallback-uv-first-pyth
description: sync-agent-configs PyYAML fallback: uv-first, python3-fallback, fail-closed
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell, reproducibility, yaml, safety]
---

Adversarial review of #2775 found that preferring system `python3` over `uv run --with pyyaml` breaks reproducibility across sibling machines. Pattern: `run_config_python` tries `uv run --with pyyaml --no-project python` first, falls back to `python3` only when uv absent and PyYAML already installed, returns nonzero on any YAML error (fail-closed, never silently skip).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
