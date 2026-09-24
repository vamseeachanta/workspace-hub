---
name: crossprovider codex content-based-routing-overrides-folder-label-ded
description: Content-based routing overrides folder label; dedupe searches target domain
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dedupe-routing, domain-classification, routing-logic]
---

PDFs filed in API/ISO folders often belong in marine/production/drilling by actual topic. Dedupe grep must search the inferred target domain, not source folder, to avoid both false-negatives (missed existing pages) and false-positives (creating duplicates in wrong domain).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
