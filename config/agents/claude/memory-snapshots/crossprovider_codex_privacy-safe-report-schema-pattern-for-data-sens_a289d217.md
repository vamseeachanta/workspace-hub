---
name: crossprovider codex privacy-safe-report-schema-pattern-for-data-sens
description: Privacy-safe report schema pattern for data-sensitive domains
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy, data-handling, report-generation, schema-contract]
---

When generating public reports from private sources, enforce a strict contract: aggregate-only counts, opaque row handles, nonliteral HMAC commitments, schema/version metadata, and source-family summaries. Never emit literal source identity fields, document names, private path fragments, raw digests, or source text. Verify this contract via leakage tests over JSON, HTML, plans, prompts, and comments before approving.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
