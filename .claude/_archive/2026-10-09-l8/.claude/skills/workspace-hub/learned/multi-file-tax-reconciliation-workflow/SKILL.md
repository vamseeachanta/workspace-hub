---
name: multi-file-tax-reconciliation-workflow
description: Systematic parallel review and reconciliation of multi-document tax filings with cross-reference validation
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax-preparation", "reconciliation", "document-verification", "workflow"]
---

# Multi-File Tax Reconciliation Workflow

When reconciling complex multi-document tax filings (1099s, worksheets, cost-seg studies, depreciation schedules), invoke authoritative source files in parallel, establish a single master document as source-of-truth (e.g., tax-preparation-worksheet.yaml), then systematically verify each supporting document against that master using specific cross-references (EIN, TIN, account numbers, line items). Document reconciliation gaps and missing referenced materials (e.g., WRK-1319 cost-seg study) before proceeding to analysis. This prevents downstream errors and identifies incomplete packets early.