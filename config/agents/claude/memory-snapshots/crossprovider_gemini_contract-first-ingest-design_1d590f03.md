---
name: crossprovider gemini contract-first-ingest-design
description: Contract-first ingest design
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-ingest, design-pattern, contract-first, validation]
---

Define validation contracts (required fields, citation standards, confidence levels) and duplicate/conflict handling logic before implementing data ingest automation. This lets reviews surface semantic errors without scraper complexity and makes the ingest logic simpler.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
