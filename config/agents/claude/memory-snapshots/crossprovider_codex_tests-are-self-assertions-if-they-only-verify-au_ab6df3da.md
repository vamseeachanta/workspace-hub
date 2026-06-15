---
name: crossprovider codex tests-are-self-assertions-if-they-only-verify-au
description: Tests are self-assertions if they only verify authored strings
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, verification, quality-gates]
---

Tests that assert presence of hard-coded prose (e.g., `assert 'gap scan' in page_body`) validate the test's own text, not external requirements or evidence. Separate content-safety string checks from gate-validation: explicit tests must validate external facts (upstream URLs, public evidence, requirement gates) independently, not via substring matches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
