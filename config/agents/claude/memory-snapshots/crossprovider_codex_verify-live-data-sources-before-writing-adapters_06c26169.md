---
name: crossprovider codex verify-live-data-sources-before-writing-adapters
description: Verify live data sources before writing adapters
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [data-discovery, adapter-design, source-verification]
---

When designing data adapters, verify live source shapes directly via curl/HTTP before coding. Distinguish 'available via API' from 'PDF/HTML/static files requiring extraction.' Many legacy sources are not SaaS-style APIs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
