---
name: crossprovider hermes stale-review-artifacts-create-false-confidence-f
description: Stale review artifacts create false-confidence failures when plan SHA drifts
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [evidence-management, approval-safety, artifact-binding]
---

Review artifacts are bound to the plan file SHA at generation time. If the plan is revised after review, on-disk artifacts become stale. Operators can mistake stale artifacts for current evidence, causing premature advancement. Reports must explicitly surface 'stale on-disk artifacts for prior SHA' vs. 'no review yet' in operator-facing warnings, not just internal SHA-mismatch notes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
