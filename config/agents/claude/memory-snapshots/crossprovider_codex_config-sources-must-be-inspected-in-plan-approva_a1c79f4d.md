---
name: crossprovider codex config-sources-must-be-inspected-in-plan-approva
description: Config sources must be inspected in plan approval
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [configuration, plan-completeness, schema]
---

Plans editing configuration-dependent features (plugin management, MCP settings, hooks) must cite and inspect actual config schema/source files. Plans with 'tbd' paths or that skip schema inspection are under-specified and not implementation-ready.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
