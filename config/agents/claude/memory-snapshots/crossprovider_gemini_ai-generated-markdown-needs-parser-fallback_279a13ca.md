---
name: crossprovider gemini ai-generated-markdown-needs-parser-fallback
description: AI-generated markdown needs parser fallback
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [markdown, parsing, ai-generated, resilience]
---

Parsers for AI-generated markdown should gracefully degrade to raw rendering on malformation instead of failing, since AI markdown is inconsistently formatted. This maintains pipeline stability.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
