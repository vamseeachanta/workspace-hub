---
name: crossprovider codex fail-closed-data-field-denylists-require-paramet
description: Fail-closed data-field denylists require parametrized alias/synonym coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security-patterns, data-leakage-prevention, test-design]
---

Simple field-name denylists (e.g., rejecting only `source_body`, `pdf_text`) miss common aliases like `source_text`, `raw_content`, `page_text`. Use parametrized tests that cover likely synonyms and preferably validate against a normalized key pattern (e.g., `source|pdf|raw` + `text|body|content`).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
