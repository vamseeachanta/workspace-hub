---
name: crossprovider codex runtime-and-launcher-choices-must-be-fixed-and-j
description: Runtime and launcher choices must be fixed and justified in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, execution, policy]
---

Plans should not defer runtime choices (e.g., bare python3 vs uv-run, launcher selection) to execution time. The choice must be fixed and the justification explicitly stated in the plan. This applies especially to policy-enforcement work where runtime selection affects compliance metrics.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
