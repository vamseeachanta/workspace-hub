---
name: crossprovider codex validators-for-privacy-critical-fields-must-be-f
description: Validators for privacy-critical fields must be fail-closed, not fail-open
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [validator, privacy, testing]
---

A validator that only rejects a narrow denylist or sentinel list is a privacy hazard — especially for count_bucket, extension_bucket, taxonomy/class fields, discipline, workflow_signal. Test with synthetic probes (raw names, emails, exact counts, file paths in allowed fields). Sentinel-only tests don't prove privacy behavior; llm-wiki #729 validator accepted unsafe values that tests missed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
