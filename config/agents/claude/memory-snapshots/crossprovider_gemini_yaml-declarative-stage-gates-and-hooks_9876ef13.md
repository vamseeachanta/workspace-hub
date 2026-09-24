---
name: crossprovider gemini yaml-declarative-stage-gates-and-hooks
description: YAML-declarative stage gates and hooks
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [architecture, declarative, stage-lifecycle]
---

Enforcement rules defined as YAML fields (`pre_exit_hooks`, `pre_enter_hooks`, `checklist`, `tools_activated`) in stage files. Generic scripts execute YAML declarations. Optional fields enable incremental adoption and backward compatibility.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
