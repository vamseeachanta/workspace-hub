---
name: crossprovider codex fail-closed-design-for-project-specific-paramete
description: Fail-closed design for project-specific parameters in standards APIs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [api-design, standards-implementation, error-handling]
---

Don't use 0.0 or None sentinels for project-specific config (min thickness, holiday-detection voltages, etc.). Require explicit caller input; public libraries expose None, and functions raise if required params are missing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
