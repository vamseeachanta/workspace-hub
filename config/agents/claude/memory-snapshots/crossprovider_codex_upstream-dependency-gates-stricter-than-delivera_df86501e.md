---
name: crossprovider codex upstream-dependency-gates-stricter-than-delivera
description: Upstream dependency gates stricter than deliverable create blocking ambiguity
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-review, dependency-gates, scope-mismatch]
---

Plans depending on upstream completion often specify vague gates ("has landed X" or "structured findings") stricter than what upstream approved plans actually commit to. #605 requires #500 to provide "structured finding/severity API" but #500's approved artifact only defines exception-raising helpers. Gate definitions must align with upstream acceptance criteria or risk permanent blocking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
