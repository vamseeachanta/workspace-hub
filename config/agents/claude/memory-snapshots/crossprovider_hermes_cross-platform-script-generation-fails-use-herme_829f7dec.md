---
name: crossprovider hermes cross-platform-script-generation-fails-use-herme
description: Cross-platform script generation fails; use hermes_tools.terminal for safe collection
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, scripting, cross-platform, windows, tooling]
---

Direct Bash+PowerShell script generation in probe scripts fails due to syntax mixing and quoting errors. Safe fallback: use hermes_tools.terminal for structured terminal collection of Hermes/Gateway/GitHub status. Windows SSH probes via local Bash unreliable; prefer tool-based collection.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
