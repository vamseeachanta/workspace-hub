---
name: TX Franchise Tax 2026 Filing
description: TX franchise tax filings completed for AceEngineer and SKEstates — key lessons on passive entity eligibility and EZ Computation Report
type: project
originSessionId: acace9e5-c9b3-4197-828c-1c26de5bea0a
---
TX franchise tax (2026 Annual EZ Computation Report) filed for both C-Corps on 2026-04-16/17. GitHub issue #2295.

| Entity | Submission ID | Revenue | Tax Due |
|--------|-------------|---------|---------|
| Achanta AceEngineer Inc (32051090721) | 87900010 | $361,410 | $0.00 |
| Sabitha & Krishna Estates Inc (32100417123) | 87904083 | $50,086 | $0.00 |

**Why:** Both under $2,470,000 no-tax-due threshold. Due date was 2026-05-15.

**How to apply:**
- C-Corps are NOT eligible for passive entity status under TX Tax Code Ch. 171 — only partnerships/trusts qualify. The Comptroller's Webfile system enforces this with an error.
- Since 2024, entities below threshold use "EZ Computation Report" (not the old "No Tax Due Information Report")
- SKEstates revenue goes in "Rents" field (NAICS 531120, NNN lease income)
- AceEngineer Webfile number: XT710045; SKEstates: XT036957
- eSystems (React/MUI) requires manual keyboard typing for inputs — JS `.value` doesn't satisfy React validation
- Traditional Webfile (mycpa.cpa.state.tx.us) uses standard HTML forms — JS filling works fine
- Confirmations saved at `taxes/2025/filed/tx-franchise-tax-confirmation-2026.md` in each repo
