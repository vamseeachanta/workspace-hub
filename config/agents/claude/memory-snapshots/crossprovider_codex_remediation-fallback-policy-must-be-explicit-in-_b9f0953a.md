---
name: crossprovider codex remediation-fallback-policy-must-be-explicit-in-
description: Remediation fallback policy must be explicit in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [package-management, reproducibility, acceptance-criteria]
---

When target versions are unavailable (apt version missing, npm unpublished), the plan must state upfront: auto-install current-channel + log exception, or fail-hard. Leaving fallback undefined causes non-deterministic outcomes and review churn. Parity acceptance criteria must account for the fallback policy (e.g., 'except where version unavailable').

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
