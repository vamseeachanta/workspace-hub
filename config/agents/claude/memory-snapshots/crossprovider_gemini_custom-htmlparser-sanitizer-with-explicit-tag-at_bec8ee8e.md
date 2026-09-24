---
name: crossprovider gemini custom-htmlparser-sanitizer-with-explicit-tag-at
description: Custom HTMLParser sanitizer with explicit tag/attribute whitelisting
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [html-sanitization, security, dependency-reduction, generalizable-pattern]
---

When external HTML sanitization libraries create dependency or supply-chain friction, roll a custom `HTMLParser` subclass that maintains explicit allowed-tags and allowed-attributes sets, validates URL schemes (http/https/mailto), and escapes all text content. Avoids regex-based approaches and provides tight control over sanitization rules.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
