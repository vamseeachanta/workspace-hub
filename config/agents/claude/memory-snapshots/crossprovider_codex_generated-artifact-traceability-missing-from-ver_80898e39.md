---
name: crossprovider codex generated-artifact-traceability-missing-from-ver
description: Generated artifact traceability missing from verification surface
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, verification, traceability]
---

Extracted CSVs listed in manifests but NOT wired into _verification-queue.csv or source-page verification metadata. Consumers cannot audit Table ID back to PDF page, caption, parse status. Fix: every extracted table needs _verification-queue.csv row + page/caption/parse-status/CSV-link metadata on source page.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
