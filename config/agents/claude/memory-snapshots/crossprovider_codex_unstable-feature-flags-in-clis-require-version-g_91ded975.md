---
name: crossprovider codex unstable-feature-flags-in-clis-require-version-g
description: Unstable feature flags in CLIs require version-gating before fleet rollout
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, configuration, deployment]
---

Features marked under-development in source (e.g., `default_mode_request_user_input` in Codex 0.146.0) may be disabled by default and absent from public docs. Fleet rollout must verify installed version on each machine; do not assume uniform availability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
