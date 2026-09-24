---
name: crossprovider codex config-drift-audit-requires-three-layers-canonic
description: Config drift audit requires three layers: canonical, user, repo-local
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration-audit, config-layering, drift-detection]
---

Full configuration audit spans canonical repo source (e.g., config/agents/codex/config.toml), user machine config (~/.codex/config.toml), and repo-local override (.codex/config.toml). Each layer can enable/disable independently; audit all three to detect drift or incomplete rollout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
