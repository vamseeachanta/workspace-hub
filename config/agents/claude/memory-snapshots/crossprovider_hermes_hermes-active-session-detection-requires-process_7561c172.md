---
name: crossprovider hermes hermes-active-session-detection-requires-process
description: Hermes active session detection requires process liveness check
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-operations, session-state, monitoring]
---

Session file existence in `~/.hermes/sessions/` does not indicate active use; historical sessions leave files behind. True discriminator for active sessions is membership in `pgrep` output for running workers, cross-checked against session_id. Grep-only searches yield false positives.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
