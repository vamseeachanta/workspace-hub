---
name: financial-data-export-workflow
description: Structured process for exporting and analyzing multi-year brokerage transaction history when browser automation is blocked
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["finance", "data-export", "fidelity", "portfolio-analysis"]
---

# Financial Data Export & Historical Analysis Workflow

When browser automation is blocked on financial sites (e.g., Fidelity), use manual CSV export + historical archive strategy: (1) Export current YTD transactions from the brokerage UI; (2) Locate historical transaction files already downloaded in data repo (e.g., `achantas-data/_finance/fidelity/`); (3) Build a parsing script that handles CSV format variations across years; (4) Aggregate transaction data to compute net positions, cost basis, and portfolio composition. This bypasses browser restrictions while enabling full multi-year analysis.