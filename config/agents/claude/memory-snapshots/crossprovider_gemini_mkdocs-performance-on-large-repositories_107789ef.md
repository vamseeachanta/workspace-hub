---
name: crossprovider gemini mkdocs-performance-on-large-repositories
description: MkDocs performance on large repositories
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [mkdocs, documentation, ci-performance]
---

MkDocs + mkdocstrings (griffe backend) can experience significant build time and memory pressure on repositories with 1,000+ files. Profile builds on large repos early in planning; implement CI caching for MkDocs and ensure griffe can access installed dependencies for accurate type resolution.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
