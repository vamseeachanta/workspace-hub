---
name: crossprovider gemini drift-classification-precedence-prevents-audit-f
description: Drift classification precedence prevents audit false positives
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [audit, classification, reporting]
---

Check non-actionable buckets (symbolic, external, sibling_repo, non_repo_artifact) before repo-local to prevent generated-site paths inflating counts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
