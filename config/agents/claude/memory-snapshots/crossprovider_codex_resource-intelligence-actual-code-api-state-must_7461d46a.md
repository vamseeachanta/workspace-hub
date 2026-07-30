---
name: crossprovider codex resource-intelligence-actual-code-api-state-must
description: Resource Intelligence (actual code/API state) must precede adversarial plan review
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [plan-review, verification, evidence-based]
---

Plans that cite files or APIs should be grounded first—verify the code actually exists at HEAD, that behavior claims are current, and that tool invocations work. Treating citations as assertions to verify (not facts) catches stale plans and false assumptions. Example: plan #74 checked Hugging Face immutability via direct API call before incorporating it into the design.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
