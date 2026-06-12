---
name: crossprovider hermes corpus-manifest-validators-are-blind-to-changes-
description: Corpus manifest validators are blind to changes after first 12k chars
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [rag-validation, llm-wiki, validation-bypass]
---

Hash verification in RAG validators only covers initial corpus-manifest entries; real content beyond ~12k bytes per file is never hashed/verified, allowing stale or forged artifacts to pass validation. Solution: compute and store full-file token_sha256 or structured block hashing to cover entire corpus.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
