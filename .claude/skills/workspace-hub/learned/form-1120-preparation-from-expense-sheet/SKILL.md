---
name: form-1120-preparation-from-expense-sheet
description: Map cash-basis expense sheet to Form 1120 schedules for C-Corp tax filing, including revenue reconciliation, Schedule L balance sheet reconstruction without prior returns, and gap identification.
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["corporate-tax", "form-1120", "cash-basis", "tax-filing"]
---

# Form 1120 Preparation from Expense Sheet

When a client provides an expense sheet as source-of-truth for a C-Corp cash-basis filing but lacks prior-year returns or complete bank records: (1) validate revenue/expense totals against the expense sheet, (2) map each expense line to the appropriate Form 1120 schedule (COGS, compensation, deductions, etc.), (3) build Schedule L balance sheet by reconstructing BOY balances from known entity facts (incorporation date, loan amounts, retained earnings assumptions), (4) identify critical gaps (bank balances on 1/1 and 12/31, capital stock, prior retained earnings, estimated tax payments) and request them explicitly, (5) confirm filing tool supports Form 1120 (FreeTaxUSA does not).