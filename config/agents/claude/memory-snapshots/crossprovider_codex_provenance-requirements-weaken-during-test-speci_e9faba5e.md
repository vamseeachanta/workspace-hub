---
name: crossprovider codex provenance-requirements-weaken-during-test-speci
description: Provenance requirements weaken during test specification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [provenance, test-spec, acceptance-criteria]
---

When an issue requires specific provenance fields (source_title, source_url, page_reference, quoted_text, confidence), the tests later weaken to 'page reference or quote' validation. Lock provenance requirements in tests at the same specificity as the issue claim; use test fixtures with all required fields present.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
