---
name: crossprovider codex thin-evidence-in-plans-should-trigger-review-fin
description: Thin evidence in plans should trigger review findings: samples missing, only summary counts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [evidence-quality, verification, review-rigor]
---

Issue #2452 evidence section showed `/tmp/2452-flake8.txt` summary counts but no actual flake8 output samples or per-file breakdown. Since split strategy depended on `_cross_database_data.py` being E231-dominated, absence of sample output meant claims were unverifiable. Approval-ready evidence sections should include representative quoted output or excerpted file snippets, not just totals.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
