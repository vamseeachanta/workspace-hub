---
name: crossprovider codex stop-guard-language-must-match-actual-stage-runn
description: Stop guard language must match actual stage-runner invocation mode (task_agent vs chained)
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [skill-documentation, stage-orchestration, specification-accuracy]
---

If a skill doc says halt-don't-proceed but the stage contract runs as chained_agent, agents won't actually stop. Stop guard wording must reference the orchestration mode or stay stage-agnostic. Document/code mismatch creates execution-time contradictions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
