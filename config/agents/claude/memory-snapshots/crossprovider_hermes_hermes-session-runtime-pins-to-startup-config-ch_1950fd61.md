---
name: crossprovider hermes hermes-session-runtime-pins-to-startup-config-ch
description: Hermes session runtime pins to startup; config changes apply to new sessions only
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-agent, model-switching, session-lifecycle]
---

Long-lived Hermes sessions restore original model at each turn, so ~/.hermes/config.yaml default changes affect only new sessions. Existing sessions remain pinned to startup model. Mid-session `/model <name>` switching works; status bar shows live session runtime, not config default.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
