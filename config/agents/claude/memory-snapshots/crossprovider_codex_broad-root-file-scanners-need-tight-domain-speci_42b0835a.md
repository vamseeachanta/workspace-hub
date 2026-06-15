---
name: crossprovider codex broad-root-file-scanners-need-tight-domain-speci
description: Broad-root file scanners need tight domain-specificity filters to prevent admission bugs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, admission-logic, domain-scoping, ingestion]
---

Weak filename matching (e.g., any file containing 'AISC' + '360') admits unrelated files into domain-scoped corpora. Require disambiguating markers like edition codes or publication years; test with unrelated files matching the weak filter to catch silent admission failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
