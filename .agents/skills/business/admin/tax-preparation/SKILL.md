---
name: tax-preparation
version: "2.0.0"
category: business
description: "Prepare corporate tax documents for AceEngineer Inc (C-Corp) including federal Form 1120, Texas franchise tax, R&D credit analysis, and strategic funding planning."
type: reference
tags: [tax, 1120, C-corp, R&D, Texas, franchise-tax]
scripts_exempt: true
---

# Tax Preparation — AceEngineer Inc

## Entity Quick Reference

| Field | Value |
|-------|-------|
| Entity | Achanta AceEngineer Inc |
| EIN | 46-2870262 |
| TX Tax ID | 32051090721 |
| TX SOS File # | 801789942 |
| TX Webfile # | XT710045 |
| Type | C-Corp (21% flat rate) |
| Incorporated | 2013-05-24 |
| Address | 11511 Piping Rock Dr, Houston, TX 77077 |
| Accounting Method | Cash |
| FYE | 12/31 |

## Trigger Conditions

Activate when the user mentions:
- Tax preparation or tax documents
- Corporate tax forms (1120)
- R&D budget or R&D credit
- Texas franchise tax
- Officer compensation or payroll tax
- Tax-year financial analysis

## Data Sources

### Primary Inputs
- `Sabitha/<YEAR>/EXPENSES Jan <YEAR>-Dec <YEAR> rev1.xlsx` — annual expense workbook (Income Statement sheet has all monthly revenue + expense line items)
- `invoices/` — client invoices by project
- `admin/loans/borrow/` — shareholder loan agreements
- `preferred_vendor/DiSYS/` — S-Corp analysis forms, historical references

### Tax Reference
- `taxes/<YEAR>/document-checklist.yaml` — master document tracking
- `Tax/` — historical filed returns and tax forms

### Generated Analysis (created during session)
- `taxes/<YEAR>/2025-corporate-tax-analysis.yaml` — 3-scenario tax computation
- `taxes/<YEAR>/2025-ai-rd-budget-strategy.yaml` — AI R&D budget + QRE classification
- `taxes/<YEAR>/2025-retained-earnings-ai-growth-model.yaml` — 5-year funding model

## Workflow

### Phase 1: Revenue Reconciliation
1. Read Income Statement sheet from expense workbook
2. Sum revenue by client (D=Jan through O=Dec, P=Yearly Total)
3. Cross-reference against invoice files in `invoices/`
4. Flag any discrepancies between expense sheet and checklist

### Phase 2: Expense Extraction
1. Parse Income Statement — row-by-row with column P yearly totals
2. Key line items: R&D expenses, employee salary, utilities, office supplies, phone, housekeeping
3. Note zero-value categories (server_cost, software, travel, mileage, etc.)
4. Check for home office utilities that need allocation (simplified $1,500 vs actual %)

### Phase 3: Tax Scenario Computation
Compute three scenarios — ALWAYS run all three:
1. **Standard** — all expenses as §162 ordinary deductions
2. **§174 Full** — all R&D amortized over 5yr domestic (half-year Y1 = /5/2)
3. **Hybrid** — split R&D: client-related = §162, product/AI = §174

### Phase 4: R&D Strategy Analysis
Key classifications under IRC §174 and §41:
- §174 SRE (capitalized, 5yr domestic): AI tools, digitalmodel, automation frameworks
- §162 (ordinary deduction): engineering tools used for client projects
- §41 QRE (R&D credit): wages for R&D services + 65% of contractor wages
- CRITICAL: Owner labor does NOT count as QRE unless paid W-2 wages
- Post-2022: §174 amortization is MANDATORY, not optional

### Phase 5: Funding/Capital Planning
Reverse-engineering from target:
1. Required tax → required taxable income (= target_tax / 0.21)
2. Required deductions = revenue - required taxable income
3. Gap = required deductions - documented deductions
4. Map gap to realistic categories (contractors, equipment, professional services)
5. Calculate §174 impact on Year 1 deduction (only 1/10th of R&D is deductible Y1)

### Phase 6: Filing Documents
Create these deliverables:
- `taxes/<YEAR>/2025-corporate-tax-analysis.yaml` — full scenario table
- `taxes/<YEAR>/2025-ai-rd-budget-strategy.yaml` — R&D roadmap, QRE classification, budget scenarios
- `taxes/<YEAR>/2025-retained-earnings-ai-growth-model.yaml` — 5-year funding model, capital sources
- GitHub issues for tracking: filing, payment, loan conversion, R&D program

## R&D Credit Quick Reference (Form 6765)

### Qualifying Research Expenses (QREs)
- Owner W-2 wages for R&D time (percentage of salary × % R&D time)
- Contractor wages: 65% of payments count (IRC §41(b)(3) cap)
- Supplies used in research
- Cloud/compute for research: ORDINARY deduction, NOT QRE
- Software subscriptions: ORDINARY deduction, NOT QRE
- Hardware: §179 deduction, NOT QRE

### Alternative Simplified Credit (ASC) Method
- 14% of current QREs exceeding 50% of average prior 3-year QREs
- If no prior history: 6% of current QREs (simplified base amount = 0)
- Example: $80K QRE wages + $40K contractor (×65%) = $106K QRE
  - No history → credit = 6% × $106K = $6,360
  - With 3yr history → ASC = 14% × (QREs - 50% avg) = higher

## Key Tax Strategy Notes

### §531 Accumulated Earnings Tax Defense
- C-Corps face 20% penalty on retention beyond reasonable business needs
- Strong defense: loan repayment obligations + R&D investment plans
- Document the business purpose for retaining earnings

### Officer Compensation
- $0 officer comp on C-Corp with revenue = IRS audit trigger
- Must start W-2 salary to unlock R&D credit and retirement benefits
- Cannot retroactively pay W-2 for a prior year

### Loan-to-Equity Conversion
- Convert related-party debt to equity to eliminate imputed interest
- Not a taxable event (conversion, not forgiveness)
- Provides permanent capital for business use
- Formal agreement + board resolution required

### Common Pitfalls
- Never classify all R&D as §162 when §174 applies (mandatory capitalization)
- Never treat loan principal as deductible expense
- Cannot retroactively create deductions for prior years
- §174 amortization reduces Year 1 deduction (only 1/10th deductible)
- Subcontractor payments to India = no 1099-NEC, but still fully deductible COGS

## Filing Deadlines

| Deadline | Action |
|----------|--------|
| Apr 15 | Form 1120 due (or Form 7004 extension to Oct 15) |
| Apr 15 | Estimated tax payment due |
| May 15 | Texas Franchise Tax due |
| Ongoing | Quarterly estimated tax payments (if required) |
