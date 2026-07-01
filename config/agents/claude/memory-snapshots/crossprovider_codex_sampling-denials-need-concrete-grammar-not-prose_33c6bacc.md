---
name: crossprovider codex sampling-denials-need-concrete-grammar-not-prose
description: Sampling denials need concrete grammar, not prose lists
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [sampling-safety, test-coverage, validation-grammar]
---

Prose constraints ('no custom loops', 'no unbounded crawls') cannot reliably validate arbitrary Python/shell code. Sampling control requires deny-list of concrete command patterns (json.load, .read_text(), grep variants, wc, sha256sum) plus deny fixtures for each.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
