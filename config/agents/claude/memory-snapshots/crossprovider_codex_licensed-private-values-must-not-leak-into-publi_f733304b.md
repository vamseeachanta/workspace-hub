---
name: crossprovider codex licensed-private-values-must-not-leak-into-publi
description: Licensed private values must not leak into public test fixtures
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [testing-strategy, security, private-data]
---

When integrating private/licensed data (e.g., AMJIG thresholds from `LLM_WIKI_PATH`), tests must prove getters fail-closed without that env var and never embed licensed numbers in public/committed fixtures. Separate private-value tests from public exemplars to prevent accidental disclosure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
