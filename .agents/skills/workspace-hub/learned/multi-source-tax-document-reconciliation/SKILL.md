---
name: multi-source-tax-document-reconciliation
description: Verify generated tax forms against source documents by line-by-line comparison, not just totals
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax", "verification", "reconciliation", "forms"]
---

# Multi-Source Tax Document Reconciliation

When building tax forms from multiple source documents (1099s, HUD statements, worksheets, loan agreements), verify each line item individually against the authoritative source, not just the final total. Settlement charges and similar itemized sections are common error points where the total can be correct while individual line items are wrong — this matters because the IRS may cross-reference against original documents like HUD-1 statements. Always reconcile the packet structure (identity, filing deadline, entity formation docs, cost-seg studies) before proceeding to form preparation.