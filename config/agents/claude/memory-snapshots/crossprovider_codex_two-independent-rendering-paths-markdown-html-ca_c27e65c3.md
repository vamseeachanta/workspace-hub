---
name: crossprovider codex two-independent-rendering-paths-markdown-html-ca
description: Two independent rendering paths (Markdown + HTML) cause silent drift
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [rendering-architecture, single-source-of-truth, drift-prevention]
---

When Markdown and HTML are rendered separately from a shared data structure instead of HTML being derived from the Markdown, structural changes diverge over time because changes to one rendering path don't propagate to the other. Render HTML from the Markdown output or use a single canonical intermediate model.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
