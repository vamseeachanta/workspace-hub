---
name: crossprovider codex minified-json-defeats-defect-traceability
description: Minified JSON defeats defect traceability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract-design, review-methodology, traceability]
---

When contract/spec files are minified to single lines, file:line citations collapse to meaningless references (all rows → line 1), breaking reviewer ability to pinpoint issues. Reviewers using exact file:line references lose traceability; plan for human-readable formatting in critical contract files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
