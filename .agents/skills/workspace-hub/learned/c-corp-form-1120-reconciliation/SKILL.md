---
name: c-corp-form-1120-reconciliation
description: Reconcile multi-source corporate tax data to prepare Form 1120 using expense sheet as authoritative source
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax", "form-1120", "reconciliation", "corporate", "accounting"]
---

# C-Corp Form 1120 Reconciliation from Mixed Sources

When reconciling corporate tax filings from multiple conflicting sources (invoices, bank deposits, expense sheets), establish a single authoritative source—typically the cash-basis expense sheet prepared from actual bank activity. Map each expense line item to specific Form 1120 schedules (J, K, L, M-1). Identify critical missing data gaps (beginning-of-year balances, capital structure, bank balances) and determine whether the return can file without them. Use this workflow: (1) declare source of truth, (2) line-by-line mapping to form, (3) gap analysis with must-have vs. can-assume fields, (4) select appropriate filing tool (FreeTaxUSA ≠ 1120; use IRS PDF, Otto, or professional software).