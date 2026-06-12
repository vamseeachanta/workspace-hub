---
name: crossprovider gemini workflow-step-insertion-timing-matters
description: Workflow step insertion timing matters
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [workflow-design, state-management, lifecycle-hooks]
---

Pre-lifecycle steps (e.g., brainstorming before archive) belong BEFORE state change (file move), while context is fresh and user can abort. Post-lifecycle steps (e.g., brochure check) stay after. Timing affects whether step gates the action (pre) or is informational (post). Design scripts as separate callables rather than inline to preserve responsibility separation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
