---
name: corporate-tax-filing-reconciliation
description: Reconcile multi-document tax packets and build line-by-line IRS filing guides for first-year C-Corps with real-estate holdings
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax", "corporate-filings", "reconciliation", "real-estate", "form-1120"]
---

# Corporate Tax Filing Reconciliation

When reconciling a complete tax packet (1099s, HUD settlement, depreciation schedules, loan docs, worksheets): (1) Read all authoritative source files in parallel to establish ground truth; (2) Cross-verify line items against original documents (1099 boxes, HUD settlement charges, loan structure) — totals matching is insufficient; (3) Identify and resolve data gaps (balance sheet, property-tax allocation, related-party transactions) by reading formation/loan agreements; (4) Build forms in dependency order (Schedule L → Form 8825 → Form 4562 → Form 1120) so each line-item references can flow backward. Flag short tax years and cost-seg study support early.