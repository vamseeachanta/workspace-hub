---
name: crossprovider codex codex-yolo-configuration-precedence
description: Codex YOLO configuration precedence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [codex, configuration, tooling-quirk]
---

Global YOLO requires two settings in ~/.codex/config.toml: `approval_policy = "never"` and `sandbox_mode = "danger-full-access"`. Precedence is CLI flag > project .codex/config.toml > profile > user config, so repo-local overrides can defeat global defaults—use a shell wrapper (`command codex --yolo`) in workspace-managed bashrc if unconditional enforcement is needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
