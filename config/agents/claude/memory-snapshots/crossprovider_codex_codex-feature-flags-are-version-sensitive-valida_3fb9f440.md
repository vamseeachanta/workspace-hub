---
name: crossprovider codex codex-feature-flags-are-version-sensitive-valida
description: Codex feature flags are version-sensitive; validate against installed CLI version
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [codex, version-gates, cli-config]
---

`default_mode_request_user_input` is under development in Codex 0.146.0 and disabled by default. When planning config rollouts, verify the feature against the actual installed version; assume features listed as 'under development' may not be present in older CLI versions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
