---
name: crossprovider codex download-workflows-must-validate-downloaded-cont
description: Download workflows must validate downloaded content, not just HTTP status
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [downloads, validation, resilience]
---

WAF/paywall systems return HTTP 200 with HTML error pages masquerading as PDFs. Post-download validation (file magic bytes, PDF header check, or minimal content inspection) is needed to detect silent fetch failures. Also ensure workflow templates match their stated step descriptions; a template that only handles hard-coded URLs will not perform the documented crawl/extraction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
