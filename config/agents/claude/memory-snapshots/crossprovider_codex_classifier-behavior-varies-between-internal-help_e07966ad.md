---
name: crossprovider codex classifier-behavior-varies-between-internal-help
description: Classifier behavior varies between internal helpers and main paths — no tests catch discrepancies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [classifier-coherence, helper-mismatch, integration-testing]
---

A helper function like `_has_report_evidence()` may recognize merged ranges as report evidence, but the main classifier routes merged-only evidence as `data` unless other conditions hold. Test internal helpers separately and verify their outputs integrate correctly into main classification paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
