---
name: corporate-tax-filing-reconciliation
description: Reconcile multi-document corporate tax packets, verify line-item accuracy against source documents, and coordinate parallel form generation for same-day filing
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax-filing", "corporate-tax", "reconciliation", "form-1120", "multi-document-verification"]
---

# Corporate Tax Filing Reconciliation

When reconciling a corporate tax packet with multiple authoritative sources (1099s, settlement statements, loan docs, worksheets), verify line-by-line against source docs—not just totals—since totals can match while individual items are wrong. Load all source files in parallel, establish a master reconciliation document, then use parallel task agents to generate dependent forms (1120, 8825, 4562, Schedules). Always rebuild the balance sheet from first principles using loan agreements, capital structure, and cash flows. Flag data gaps (e.g., property-tax allocation) that require separate source documents before forms lock.