---
name: crossprovider gemini byte-equality-assertion-vs-brittle-content-count
description: Byte-equality assertion vs brittle content counting in tests
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [acceptance-criteria, testing, robustness, brittle-tests]
---

In acceptance criteria, replace fragile assertions like 'body contains all 39 entries' with byte-equality against reference digest. Stable across upstream edits; unambiguous on pass/fail. Applied to sitemap validation in #2357.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
