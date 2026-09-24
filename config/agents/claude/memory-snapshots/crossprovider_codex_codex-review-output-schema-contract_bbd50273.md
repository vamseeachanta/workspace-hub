---
name: crossprovider codex codex-review-output-schema-contract
description: Codex review output schema contract
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, review-schema, structured-output]
---

Codex reviews must validate against a JSON schema with fields: verdict, summary, issues_found (array), suggestions (array), questions_for_author (array). Downstream tools (validate-review-output.sh, render-structured-review.py) depend on this structure; deviations break validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
