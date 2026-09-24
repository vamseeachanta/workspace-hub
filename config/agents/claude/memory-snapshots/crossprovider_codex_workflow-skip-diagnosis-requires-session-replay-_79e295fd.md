---
name: crossprovider codex workflow-skip-diagnosis-requires-session-replay-
description: Workflow skip diagnosis requires session replay and bypass-mode classification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [debugging-methodology, workflow-analysis, diagnosis]
---

When diagnosing why agents bypass a gate, replaying observed session trails is essential to confirm the mechanism: distinguish between unclear step wording that agents misinterpret versus tool-call momentum that overrides the stop point. Document the specific bypass mode before implementing fixes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
