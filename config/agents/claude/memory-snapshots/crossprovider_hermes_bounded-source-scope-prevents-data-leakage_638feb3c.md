---
name: crossprovider hermes bounded-source-scope-prevents-data-leakage
description: Bounded source scope prevents data leakage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, data-classification, security]
---

Source scope in graph manifests must be bounded to public-safe wiki/source-map artifacts only, never private/raw corpora. This is a classification safety gate that prevents sensitive data from being implicitly promoted to public surfaces. Document this constraint explicitly in schema docs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
