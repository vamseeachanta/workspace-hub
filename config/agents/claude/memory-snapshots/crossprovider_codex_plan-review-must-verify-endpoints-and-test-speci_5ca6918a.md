---
name: crossprovider codex plan-review-must-verify-endpoints-and-test-speci
description: Plan review must verify endpoints and test specifications, not just prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, adversarial-review, verification]
---

Adversarial plan review should check file existence, command syntax, endpoint sensitivity (e.g., do not copy CGNAT IPs into runbook prose), and test feasibility. First-round findings often expose structural defects like self-blocking test specs or artifact naming inconsistencies that require design fixes before implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
