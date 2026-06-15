---
name: crossprovider codex llm-refuses-copyright-reproduction-deterministic
description: LLM refuses copyright reproduction; deterministic tools don't
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [copyright, extraction, tooling-choice]
---

Claude agents refuse to reproduce copyrighted text verbatim, even into private repos. Deterministic tools like PyMuPDF have no such constraint and are the correct approach for full-fidelity private corpus ingest. Use tools, not models, for mechanical extraction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
