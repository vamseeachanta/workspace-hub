---
name: corporate-tax-filing-reconciliation
description: Systematic workflow for preparing and reconciling multi-year corporate tax filings with missing prior returns
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["corporate-tax", "filing-preparation", "reconciliation", "missing-documents"]
---

# Corporate Tax Filing Reconciliation

When filing current-year taxes with missing prior-year returns, establish a parallel-load strategy: invoke the relevant tax skill first, then systematically read primary source files (balance sheet, P&L, payroll registers), supporting documents (invoices, loan agreements), and finally cross-reference GitHub issues for known blockers (e.g., unfiled prior years, extension deadlines). Prioritize resolving revenue discrepancies by sampling invoices and reconciling against reported totals before proceeding to deduction modeling.