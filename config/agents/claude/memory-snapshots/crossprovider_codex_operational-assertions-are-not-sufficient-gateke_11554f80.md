---
name: crossprovider codex operational-assertions-are-not-sufficient-gateke
description: Operational assertions are not sufficient gatekeeping; require schema validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [enforcement, gates, security]
---

Statements like 'we will ensure all machines have FENCE=1 enabled' are not enforceable gates. Actual enforcement requires fail-closed defaults in code, validator rules rejecting unsafe states, or required schema fields. Review blocker: if the plan says 'X is required operationally', ask whether the code actually rejects X=false or missing, or just assumes it's true.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
