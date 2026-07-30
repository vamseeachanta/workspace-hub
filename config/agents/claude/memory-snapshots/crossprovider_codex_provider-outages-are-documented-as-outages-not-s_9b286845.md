---
name: crossprovider codex provider-outages-are-documented-as-outages-not-s
description: Provider outages are documented as outages, not silent approvals
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [workflow, multi-provider, error-handling]
---

When Gemini lacks auth, Codex hits a CLI regression, or Claude times out during adversarial review, record the exact failure reason and continue without claiming success. A MAJOR verdict from fewer providers is still MAJOR; outages do not approve the plan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
