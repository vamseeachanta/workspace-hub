---
name: crossprovider codex cdn-only-assets-make-engineering-reports-unsuita
description: CDN-only assets make engineering reports unsuitable for offline use
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, html-generation, deployment]
---

Engineering reports relying on CDN assets (KaTeX for formulas, Chart.js for charts) fail in offline, air-gapped, and long-term archival scenarios. Default to self-contained output with vendored or inlined assets, or provide an explicit offline mode rather than falling back to CDN.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
