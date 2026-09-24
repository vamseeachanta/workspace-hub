---
name: crossprovider codex parse-status-defaults-to-provisional-unverified-
description: Parse status defaults to provisional-unverified for all extracted tables
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards-ingest, data-quality, liability]
---

Extracted table/figure data uses `provisional-unverified` (parsed columns not source-verified) or `raw-unverified` (layout/extraction needs manual cleanup). Never mark tables as `verified` by default; this is a liability/quality gate. Append all extraction artifacts to domain's `_verification-queue.csv`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
