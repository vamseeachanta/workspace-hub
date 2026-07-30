---
name: crossprovider codex adversarial-multi-provider-review-gates-all-plan
description: Adversarial multi-provider review gates all plan implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [planning, review-gate, multi-provider, quality-discipline]
---

Plans must pass independent adversarial review by 3+ providers (minimum 2) with zero MAJOR verdicts before implementation starts. Blockers are fixed and re-run, not worked around. Use size caps (e.g., 400 lines) and reproducible defaults (checksummed binaries, deterministic fallbacks) so external changes cannot invalidate requirements.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
