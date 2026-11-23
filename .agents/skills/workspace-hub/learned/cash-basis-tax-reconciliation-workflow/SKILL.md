---
name: cash-basis-tax-reconciliation-workflow
description: Multi-source document reconciliation to establish authoritative tax basis and complete Form 1120 for C-Corps using cash method
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["tax", "accounting", "form-1120", "reconciliation", "cash-basis"]
---

# Cash-Basis Tax Reconciliation Workflow

When filing Form 1120 for a cash-method C-Corp with conflicting revenue/expense sources: (1) identify the authoritative source (typically bank deposits/expense sheet over invoices), (2) systematically map each line to corresponding Form 1120 schedules (J, K, L, M-1), (3) identify critical gaps (BOY/EOY cash balances, capital structure, prior retained earnings) that block filing, (4) use bank statements to close Schedule L gaps, (5) flag estimated tax penalties (Form 2220) when payments were $0. Prioritize Schedule L completion since total assets >$250K triggers filing requirement.