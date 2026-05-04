---
name: blocker-reporting-outcome-validation
description: Pattern for closing issues where the deliverable is documented blockers rather than feature completion
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["issue-closure", "validation", "blocker-documentation"]
---

# Blocker-Reporting Outcome Validation

When an issue's acceptance criteria include explicit blocker documentation rather than feature completion: (1) Run existing test suite to validate ledger/index backing and content hashes; (2) Generate a blocker-reporting artifact (e.g., YAML handoff) that lists each target with its blocker reason; (3) Verify all targets have either valid summaries OR documented blockers; (4) Cross-reference artifact paths in handoff comments to #2227 or next-phase issue; (5) Close the issue with acceptance criteria met via blocker documentation, not feature delivery.