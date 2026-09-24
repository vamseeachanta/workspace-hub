---
name: crossprovider codex upstream-contract-consumption-needs-explicit-wor
description: Upstream contract consumption needs explicit wording to avoid parent/split confusion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gates, issue-dependencies, clarity]
---

Child issues that consume upstream split contracts (#65-#70) must explicitly state which splits are usable and which parent issues (#51, #61, #63) still block implementation. Naming a parent issue without saying "approved" vs. "still blocking" leaves reviewers unable to judge whether child work is actually unblocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
