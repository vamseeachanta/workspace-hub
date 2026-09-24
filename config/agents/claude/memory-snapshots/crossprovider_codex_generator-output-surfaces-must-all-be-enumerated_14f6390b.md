---
name: crossprovider codex generator-output-surfaces-must-all-be-enumerated
description: Generator output surfaces must all be enumerated in tests, not just one report format
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-coverage, generator-safety, multi-surface]
---

Issue drafts, dispatch prompts, JSON/HTML reports, and GitHub comment bodies are separate output surfaces. Covering JSON reports clean does not prove generated comments, drafts, or prompts are clean. Tests must explicitly scan every output channel that can leak identity-bearing fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
