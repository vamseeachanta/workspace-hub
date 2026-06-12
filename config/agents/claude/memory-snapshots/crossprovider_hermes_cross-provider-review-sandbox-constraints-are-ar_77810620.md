---
name: crossprovider hermes cross-provider-review-sandbox-constraints-are-ar
description: Cross-provider review sandbox constraints are architectural
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex-sandbox, gemini-local-validation, cross-provider-dispatch]
---

Codex requires inline plan content (path-only causes poor reviews), Gemini has local `.gemini/agents/*.md` validation issues, Claude may be unavailable. These are not transient but permanent sandbox/API differences. Plan review orchestration must route based on provider capability, not treat all providers as equivalent.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
