---
name: crossprovider codex optional-features-must-not-become-mandatory-scop
description: Optional features must not become mandatory scope creep
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope-management, plan-review, scheduling]
---

When a plan makes optional features (like scheduling/cron) mandatory without clear justification, that's scope creep. If optional, defer to a follow-on issue; if mandatory, justify and include full operational contracts (shell-script tests, registration mechanics, failure behavior).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
