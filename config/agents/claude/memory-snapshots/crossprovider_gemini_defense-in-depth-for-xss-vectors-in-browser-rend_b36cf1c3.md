---
name: crossprovider gemini defense-in-depth-for-xss-vectors-in-browser-rend
description: Defense-in-depth for XSS vectors in browser-rendered HTML
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [security, xss, html-rendering, defense-in-depth]
---

Even after primary sanitization (bleach or regex), explicitly strip high-risk tags (svg, math) and event handlers in separate passes. SVG/math are particular XSS vectors in browser-opened documents and warrant redundant removal.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
