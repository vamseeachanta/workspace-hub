---
name: crossprovider codex classify-before-writing-read-only-triage-catches
description: Classify before writing: read-only triage catches contamination early
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [workflow-order, quality-control, early-detection]
---

Running a read-only triage pass (extractability, encryption, routing, dedupe risk) BEFORE any wiki writes catches contamination and routing errors early. This batch saved duplicate writes and prevented mis-categorized documents from entering the corpus. Classification → routing confirmation → batch write is the pattern that worked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
