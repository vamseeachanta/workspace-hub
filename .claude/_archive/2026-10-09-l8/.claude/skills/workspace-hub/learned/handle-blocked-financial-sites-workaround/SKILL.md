---
name: handle-blocked-financial-sites-workaround
description: Workflow for accessing financial account data when browser automation is blocked on brokerage sites
version: 1.0.0
source: auto-extracted
extracted: 2026-04-13
metadata:
  tags: ["browser-automation", "financial-data", "workaround", "security"]
---

# Handle Blocked Financial Sites Workaround

When browser automation tools are blocked on financial/brokerage sites (by design for security), use data export as the primary retrieval method. Request the user to manually export CSV files from the brokerage platform (transactions, positions, gains/losses) and save them locally or in a shared directory. If manual export isn't feasible, ask for a screenshot or direct copy-paste of table data. Never attempt to circumvent security blocks on sensitive financial sites—the restrictions prevent accidental trade execution or credential exposure.