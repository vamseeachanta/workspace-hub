---
name: crossprovider codex conservative-text-based-content-filtering-in-doc
description: Conservative text-based content filtering in document ingestion
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [content-filtering, conservative-classification, ingestion-safety, text-analysis]
---

Pattern: classifier function returns None (do-not-filter) for ambiguous cases—only fire on high-confidence signals (e.g., 'yachting resume', 'Hodges Creek' + Visio, '百度文库', 'bank statement'). Require strong/multiple matches. Place the filter pre-write (after text extraction, before wiki page creation) using existing skip control flow (_record_skip). This avoids touching wiki/queue data and preserves consistency with existing error paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
