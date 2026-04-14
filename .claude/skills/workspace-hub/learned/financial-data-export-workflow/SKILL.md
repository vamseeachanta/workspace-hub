---
name: financial-data-export-workflow
description: Workflow for gathering and analyzing dispersed financial transaction data when direct API/browser access is restricted
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["finance", "data-extraction", "workflow", "csv-parsing", "multi-year-analysis"]
---

# Financial Data Export & Multi-Year Analysis Workflow

When browser automation is blocked on financial sites (safety restriction), use manual export + local parsing: (1) Request user export transactions as CSV from brokerage interface, (2) Locate historical exports already stored in project repo (e.g., `_finance/fidelity/`), (3) Write format-agnostic parser script to handle varying CSV schemas across years, (4) Synthesize complete transaction history to identify investor patterns and portfolio evolution. This preserves security while enabling analysis.