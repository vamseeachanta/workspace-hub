---
name: crossprovider gemini cross-review-provider-specific-verdicts-require-
description: Cross-review provider-specific verdicts require plan revision
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cross-review, verdicts, plan-revision]
---

When a multi-provider cross-review produces MAJOR from one provider (e.g., Codex MAJOR on 16-vs-12 domain mapping, coverage gaps), plan revision is mandatory before re-review. Different providers surface different defect classes (Claude: minor dual-write, Codex: major coverage/schema, Gemini: minor validation). Re-approval from user is required after revision.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
