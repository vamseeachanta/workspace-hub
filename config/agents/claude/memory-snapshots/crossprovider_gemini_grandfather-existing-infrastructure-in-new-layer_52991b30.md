---
name: crossprovider gemini grandfather-existing-infrastructure-in-new-layer
description: Grandfather existing infrastructure in new-layer redesigns
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [scope-management, architecture, refactoring]
---

When adding a new abstraction layer (state tracking, analysis, orchestration) on top of existing production behavior, explicitly separate new logic from grandfathered behavior. Prevents scope creep, clarifies ownership boundaries, and simplifies acceptance criteria. Apply to any system redesign that touches live infrastructure.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
