---
name: crossprovider codex reviews-scoped-to-wrk-approval-items
description: Reviews scoped to WRK approval items
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [wrk-scoping, review-gates, workflow-binding]
---

The review submission script extracts WRK IDs from file paths (regex: WRK-[0-9]+) and injects scope context into Codex prompts ('This review is being run under the active approved work item'). This ties code reviews to the authorization gates in SHARED_SOUL.md hard-gates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
