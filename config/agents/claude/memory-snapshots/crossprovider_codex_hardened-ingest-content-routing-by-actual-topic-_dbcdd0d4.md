---
name: crossprovider codex hardened-ingest-content-routing-by-actual-topic-
description: Hardened ingest: content routing by ACTUAL topic, not folder label
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, content-routing, llm-wiki, hardened-contract]
---

When ingesting documents into llm-wiki domains (engineering-standards, marine-engineering, maritime-law, etc.), classify by the document's actual content and intended use, not by the source folder name. A PDF in the ISO/ folder may be a maritime regulation, personal ID scan, or utility bill — each has a different domain and disposition. Route by content; flag or skip mismatched material.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
