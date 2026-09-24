---
name: crossprovider gemini vercel-rewrites-cannot-serve-files-outside-outpu
description: Vercel Rewrites cannot serve files outside outputDirectory
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [vercel, deployment, misconception, rewrite-routing]
---

Vercel rewrites support only same-app paths within outputDirectory or external-origin proxies—they cannot access arbitrary repo-root files outside deployed app directory. This common misconception surfaced as MAJOR finding requiring plan revision in #2391.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
