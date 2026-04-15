---
name: corporate-tax-filing-reconciliation
description: Reconcile multi-source tax documents, verify line-item accuracy against settlement/1099 records, and build audit-ready filing guides for C-Corp 1120 returns.
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax-preparation", "reconciliation", "form-1120", "document-verification", "audit-support"]
---

# Corporate Tax Filing Reconciliation

When reconciling a corporate tax filing across multiple source documents (1099s, HUD statements, depreciation studies, loan agreements), verify line-by-line totals rather than just aggregate figures—settlement charges and expense allocations are common error points where totals match but individual items don't. Load all authoritative files in parallel, cross-reference box amounts/TINs/account numbers explicitly, and identify gaps (balance sheet, property-tax allocations) before drafting forms. Use a master worksheet as the single source of truth, then build form-specific guides that show source-to-line mapping for each 1120 schedule, making audit trails explicit.