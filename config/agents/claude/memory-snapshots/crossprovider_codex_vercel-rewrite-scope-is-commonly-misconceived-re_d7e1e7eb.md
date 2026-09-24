---
name: crossprovider codex vercel-rewrite-scope-is-commonly-misconceived-re
description: Vercel rewrite scope is commonly misconceived; rewrites are not limited to outputDirectory
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [vercel, technical-misconception, documentation, option-analysis]
---

Plans often incorrectly claim Vercel rewrites cannot reach files or functions outside outputDirectory. Per current Vercel docs, rewrites can target same-application paths and external origins. This misconception recurs in Option-B rejection analysis and requires correction per https://vercel.com/docs/routing/rewrites.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
