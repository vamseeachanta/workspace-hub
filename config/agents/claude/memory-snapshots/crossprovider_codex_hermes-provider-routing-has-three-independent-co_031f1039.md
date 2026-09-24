---
name: crossprovider codex hermes-provider-routing-has-three-independent-co
description: Hermes provider routing has three independent configuration paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hermes, provider-routing, configuration]
---

Main interactive model, delegation target, and quick-command provider are separately configured in ~/.hermes/config.yaml. When troubleshooting unexpected provider defaults (e.g., Claude when Codex is expected), check all three paths since they can diverge independently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
