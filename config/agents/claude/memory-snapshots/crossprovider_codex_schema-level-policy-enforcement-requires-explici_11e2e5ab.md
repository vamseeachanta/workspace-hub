---
name: crossprovider codex schema-level-policy-enforcement-requires-explici
description: Schema-level policy enforcement requires explicit allowlist + test assertions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [policy-enforcement, testing-pattern, privacy-by-design]
---

Source-title aliasing policy (no filename, relative_path, pdfinfo_title) cannot be enforced by prose alone. Implementation must validate input-field allowlists and tests must assert rejection of forbidden fields in outputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
