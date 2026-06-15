---
name: crossprovider codex glossary-definitions-require-structural-anchorin
description: Glossary definitions require structural anchoring, not substring matching
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [testing, documentation, glossary]
---

Substring-based term testing is too brittle and weak (allows terms like 'field' to pass without real definitions). Require each term to be anchored to Markdown structure—a heading, definition-list label, or table cell—with non-empty own-words definition text.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
