---
name: crossprovider codex plans-deferring-design-decisions-should-flag-the
description: Plans deferring design decisions should flag them as blocking scope, not deferred
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [scope-clarity, design-decisions, deferral-risk]
---

Plans saying 'we'll decide whether to vendor Plotly or use CDN later' or 'strict vs production modes, TBD' are leaving correctness-critical choices unresolved. Such decisions must be made before approval, or explicitly marked as post-MVP work with acceptance criteria that do not depend on them. Deferred decisions create review ambiguity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
