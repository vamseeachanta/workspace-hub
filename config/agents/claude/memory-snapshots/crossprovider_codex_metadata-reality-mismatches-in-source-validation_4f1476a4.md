---
name: crossprovider codex metadata-reality-mismatches-in-source-validation
description: Metadata-reality mismatches in source validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [data-governance, validation, sources, api-design]
---

Systems claiming "direct official sources" must validate actual download Content-Type and format, not just URL host patterns or initial response codes. A URL returning HTML (even from an official domain) is not a direct artifact. Validation must test actual content, not metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
