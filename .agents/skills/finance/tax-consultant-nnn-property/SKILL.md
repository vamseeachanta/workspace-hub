---
name: tax-consultant-nnn-property
version: "1.0.0"
category: finance
description: "Comprehensive tax consultant for C-Corp owners of NNN (triple-net) commercial properties. Covers Form 1120 preparation, cost segregation, depreciation schedules, NOL management, 1099 reconciliation, tenant reimbursement tracking, and IRS compliance."
tags: [tax, c-corp, nnn, real-estate, depreciation, cost-segregation, 1099, nol, irs, form-1120]
type: reference
capabilities:
  - ccorp_form_1120_preparation
  - cost_segregation_analysis
  - depreciation_schedule_management
  - nol_carryforward_tracking
  - tenant_1099_reconciliation
  - nnn_reimbursement_tracking
  - tax_optimization_strategies
  - irs_compliance_guidance
requires: []
trigger: manual
context:
  entity: SKEstates Inc (Sabitha and Krishna Estates Inc)
  ein: "39-2384131"
  property: "15645 Westpark Drive, Houston TX 77082 (Family Dollar #30150)"
  tenant: "Family Dollar Stores of Texas, LLC"
  lease_type: "Modified Triple-Net (NNN)"
  tax_year_reference: "2025 (filed 2026)"
---

# Tax Consultant: NNN Commercial Property (C-Corp)

> Practical tax reference for a C-Corp owning a NNN commercial property.
> Primary context: SKEstates Inc / Family Dollar, Houston TX.
> All guidance applies broadly to any C-Corp NNN landlord.

## Quick Reference: Annual Tax Calendar

| Deadline | Action |
|----------|--------|
| Jan 31 | Pay prior-year property taxes (TX penalty-free deadline) |
| Feb 15 | Receive tenant 1099-MISC (Box 1 Rents) from national tenants |
| Mar 15 | S-Corp election deadline (Form 2553) — if reconsidering structure |
| Mar 31 | Send 1099-MISC to any vendors paid $600+ in prior year |
| Apr 15 | C-Corp Form 1120 filing deadline (or Form 7004 for 6-month extension) |
| Apr 15 | Invoice tenant for prior-year property tax reimbursement (NNN) |
| Jun 15 | Q2 estimated tax payment (Form 1120-W) if taxable income expected |
| Jul 30 | NNN reimbursement demand deadline (180 days from Jan 31 tax due date) |
| Sep 15 | Q3 estimated tax payment; extended Form 1120 due if on extension |
| Dec 31 | Year-end planning: confirm depreciation elections, NOL position |

---

## Core Topics

1. C-Corp (Form 1120) tax return preparation -- see references/form-1120-preparation.md
2. Cost segregation analysis -- see references/cost-segregation.md
3. Depreciation schedules (MACRS, bonus, §179) -- see references/depreciation-schedules.md
4. NOL carryforward management -- see references/nol-management.md
5. 1099 reconciliation procedures -- see references/1099-reconciliation.md
6. Tenant reimbursement tracking -- see references/tenant-reimbursements.md
7. Tax optimization strategies -- see references/tax-optimization.md
8. IRS compliance and audit defense -- see references/irs-compliance.md

---

## Entity Facts (SKEstates Inc)

| Field | Value |
|-------|-------|
| Entity | Sabitha and Krishna Estates Inc (dba SKEstates Inc) |
| EIN | 39-2384131 |
| Tax Form | Form 1120 (C-Corp) |
| Fed Tax Rate | 21% flat |
| State | Texas (no state income tax) |
| Tax Year | Calendar year (Jan 1 - Dec 31) |
| Property | 15645 Westpark Drive, Houston TX 77082 |
| Tenant | Family Dollar Stores of Texas, LLC (Store #30150) |
| Lease Type | Modified Triple-Net (NNN) |
| Monthly Rent | $10,141.67 |
| Annual Rent | $121,700.04 |
| Building Basis | $1,089,534 (placed in service Sept 2025) |
| Land Basis | ~$380,466 (non-depreciable) |
| Purchase Price | ~$1,470,000 (Sept 22, 2025 closing) |
| 2025 NOL | ~$105,932 (from cost segregation) |
| Lender | aceengineer (related party, 0% interest, §267 scrutiny applies) |

---

## 2025 Tax Year Summary

| Line Item | Amount |
|-----------|--------|
| Gross rental income (1099 reported) | $50,085.60 |
| Reimbursement income (taxes, insurance, HOA) | ~$19,659+ |
| Total gross receipts | ~$50,085+ |
| Property tax deduction | $29,194.58 |
| Insurance deduction | ~$10,135.92 |
| Depreciation (cost segregation) | $132,606 |
| Depreciation (standard, no cost seg) | $8,161 |
| NOL created (cost segregation path) | ~$105,932 |
| Federal tax (cost seg path) | $0 |
| Federal tax (standard path) | $4,938 |
| Texas franchise tax | $0 (below threshold) |

---

## Key Strategic Decisions Made (2025)

1. Cost segregation -- YES (self-prepared, conservative benchmarks)
2. File April 15, 2026 -- no extension needed
3. Keep C-Corp -- no S-Corp election (21% flat rate favorable for accumulation)
4. NOL stays in entity -- cannot pass to shareholders or lenders
5. No bad debt deduction -- related-party loan to solvent performing entity

---

## Pitfalls and IRS Red Flags

1. Related-party loan (§267) -- 0% interest to/from aceengineer draws scrutiny; document as legitimate
2. Self-prepared cost segregation -- keep methodology doc with IRS citations; use conservative benchmarks (<=30% reclassification)
3. Depreciation recapture on sale -- §1250 unrecaptured gain taxed at 25% on accelerated portion
4. NOL 80% limitation -- cannot use more than 80% of taxable income to offset via NOL (TCJA §172)
5. 1099 over-reporting -- tenant may include reimbursements in Box 1 Rents; always reconcile to actual payments
6. Reimbursement timing -- cash-basis entity reports reimbursements when received, not when invoiced
7. September proration -- closing-year partial ownership creates complex rent allocation; verify via bank statements + HUD
8. Insurance included in 1099 -- if tenant reimburses insurance in same year as premium paid, it is income (offset by deduction)

---

## Agent Decision Framework

When advising on NNN C-Corp tax questions, follow this triage:

INCOME QUESTION? -> references/1099-reconciliation.md
DEDUCTION QUESTION? -> references/depreciation-schedules.md or references/tenant-reimbursements.md
ENTITY STRUCTURE? -> references/tax-optimization.md
LOSS / NOL? -> references/nol-management.md
FILING MECHANICS? -> references/form-1120-preparation.md
AUDIT / COMPLIANCE? -> references/irs-compliance.md
COST SEGREGATION? -> references/cost-segregation.md
