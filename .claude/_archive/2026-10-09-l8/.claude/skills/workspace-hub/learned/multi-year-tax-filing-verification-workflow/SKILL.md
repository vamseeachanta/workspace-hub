---
name: multi-year-tax-filing-verification-workflow
description: Verify and reconcile complex multi-form tax filings by cross-referencing source documents, identifying data dependencies, and validating line-by-line against authoritative records.
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax-compliance", "document-verification", "multi-form-filing", "data-reconciliation"]
---

# Multi-Year Tax Filing Verification Workflow

When handling complex C-Corp filings with multiple forms (1120, 8825, 4562, Schedules), verify by: (1) anchoring all numbers to authoritative source documents (1099s, HUD statements, loan agreements), (2) identifying hidden dependencies (balance sheet structure, related-party transactions, settlement charges), (3) validating line-by-line totals against individual items (not just column totals—IRS cross-references detail), (4) resolving gaps systematically (ask for missing docs rather than assume), (5) committing verified files with GitHub issues as audit trail. Common error point: settlement charges and depreciation schedules match totals but fail on line-item detail.