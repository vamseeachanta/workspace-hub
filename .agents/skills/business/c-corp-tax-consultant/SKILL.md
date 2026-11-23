---
name: c-corp-tax-consultant
description: Tax optimization and filing guide for C-Corp commercial real estate entities. Covers Form 1120, cost segregation, NOL management, depreciation strategies, 1099 reconciliation, and legitimate tax minimization for NNN lease properties. Includes TX franchise tax filing procedures and direct e-filing research.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [tax, C-Corp, Form-1120, NNN, real-estate, cost-segregation, depreciation, NOL, Texas, franchise-tax, e-file]
metadata:
  hermes:
    tags: [tax, C-Corp, Form-1120, NNN, real-estate, cost-segregation, depreciation, NOL, Texas, franchise-tax]
---

# C-Corp Tax Consultant — NNN Commercial Property

Tax optimization, preparation, and filing guide for C-Corp entities owning single-tenant NNN commercial real estate.

## Quick Reference

| Item | Value |
|------|-------|
| Federal tax rate (C-Corp) | 21% flat |
| TX state income tax | None |
| TX franchise tax | Margin tax, No-tax-due if revenue < ~$2.47M |
| Depreciation building | 39-yr straight-line (nonresidential) |
| Cost seg components | 5yr personal property, 15yr land improvements |
| Bonus depreciation 2025 | 40% (TCJA phase-down: 2026=20%, 2027+=0%) |
| NOL rules | Carry forward indefinitely, 80% of taxable income limit |
| Form 1120 deadline | April 15 (or 15th day of 4th month after FY end) |
| Extension | Form 7004 (auto 2.5 months → Oct 15) |
| TX Franchise deadline | May 15 |

## When to Use This Skill

- Preparing Form 1120 for a C-Corp that owns rental real estate
- Evaluating cost segregation vs standard depreciation
- Managing NOL carryforwards
- Reconciling 1099-MISC reported income vs actual deposits
- Optimizing tax deductions for NNN properties
- Filing Texas Franchise Tax
- Researching direct e-filing options

---

## Phase 1: Pre-Filing Checklist

Before preparing Form 1120, verify:

1. **All income sources identified and quantified:**
   - Rental income (actual deposits, not just 1099)
   - Reimbursements received in calendar year (insurance, HOA, taxes)
   - Other income (late fees, etc.)

2. **1099-MISC reconciliation complete (see Phase 8):**
   - Compare 1099 Box 1 to actual bank deposits
   - Request breakdown from payer if discrepancy exists
   - Document findings — file with tax return if 1099 is wrong

3. **All deductible expenses documented:**
   - Property taxes (all taxing authorities)
   - Insurance premiums
   - Property management fees
   - HOA/POA fees
   - Professional fees (legal, accounting)
   - Repairs and maintenance
   - Depreciation (with cost seg if applicable)

4. **Basis calculations complete:**
   - Purchase price + capitalized closing costs = total basis
   - Land vs building allocation (appraisal ratio or HUD allocation)
   - IRC §164(d) adjustments for property tax proration at closing

---

## Phase 2: Cost Segregation Analysis

### Decision Framework

**When to use cost segregation:**
- Building basis > $500K (generally worthwhile)
- Entity has taxable income to offset (or plans to)
- Property will be held 5+ years

### Component Reclassification

| Component Life | Examples | Typical % | MACRS Life |
|---------------|----------|-----------|------------|
| 39-year (structure) | Walls, roof, foundation, structural framing | 65-75% | 39yr |
| 15-year (land improvements) | Parking lot, landscaping, exterior lighting, fencing | 15-20% | 15yr |
| 5-7 year (personal property) | Tenant-specific electrical, HVAC, flooring, fixtures | 10-15% | 5-7yr |

### Bonus Depreciation TCJA Phase-Down

| Year | Bonus Rate |
|------|------------|
| 2025 | 40% |
| 2026 | 20% |
| 2027+ | 0% |

**Strategy note:** 2025 is the last year of meaningful bonus depreciation. Lock in cost segregation now.

### Self-Prepared Study Approach

For simple single-tenant retail/warehouse properties:
1. Use published IRS component percentages (conservative: ≤30% total reclassification)
2. Document methodology with IRS references
3. Keep study file with tax records

IRS references:
- Rev. Proc. 87-56 (asset class lives)
- IRS Cost Segregation Audit Techniques Guide

### Real-World Example: SKEstates Inc (Family Dollar, Houston TX)

Building basis $1,089,534, placed in service Sept 2025 (month 9):

| Component | Allocation | Basis | Bonus 40% | Regular Y1 | Total Y1 |
|-----------|-----------|-------|-----------|-----------|----------|
| Structure (75%) | 39-year | $817,151 | $0 | $6,120 | $6,120 |
| Land improvements (15%) | 15-year | $163,430 | $65,372 | $3,258 | $68,630 |
| Personal property (10%) | 5-year | $108,953 | $43,581 | $10,901 | $54,482 |
| **Total** | | **$1,089,534** | **$108,953** | **$20,279** | **$129,232** |

vs Standard: $8,161 — additional deduction of $121,071 creating NOL of ~$119,784.
This shields ~$96K of 2026 income and ~$42K of 2027 income.
- IRS Cost Segregation Audit Techniques Guide

### Example Calculation

Given building basis $1,089,534, placed in service month 9:

**Standard (39yr SL):**
- Year 1: $1,089,534 × 0.749% = $8,161

**Cost Seg with 40% Bonus (2025):**
| Component | Basis | Bonus | Regular Y1 | Total Y1 |
|-----------|-------|-------|------------|----------|
| Structure (75%) | $817,151 | $0 | $6,120 | $6,120 |
| Land improvements (15%) | $163,430 | $65,372 | $3,084 | $68,456 |
| Personal property (10%) | $108,953 | $43,581 | $4,903 | $48,484 |
| **Total** | | | | **$123,060** |

vs $8,161 standard — **$114,899 additional deduction**

---

## Phase 3: Form 1120 — Key Lines

### Income Section (Page 1)

| Line | Description | What Goes Here |
|------|-------------|---------------|
| 1a | Gross receipts/sales | (not applicable for pure rental) |
| 5 | Gross rents | **PRIMARY — rental income received** |
| 6 | Other income | Late fees, insurance proceeds |
| 7 | Total income | Sum of 1a–6 |

### Deductions (Schedule A, Page 2)

| Line | Description | Common NNN Items |
|------|-------------|-----------------|
| 5 | Taxes and licenses | Property taxes |
| 8 | Depreciation | From Form 4562 |
| 12 | Employee benefit programs | Health insurance |
| 13 | Other deductions | Insurance, HOA, mgmt fees, professional fees |

### Required Forms

- Form 1120 (main return)
- Form 8825 (Rental Real Estate Income and Expenses)
- Form 4562 (Depreciation and Amortization)
- Schedule K (Shareholders' Stock and Debt)
- Schedule M-1 (Book-Tax Reconciliation, if required)

---

## Phase 4: NOL Management

### TCJA Rules (Post-2017)

- NOLs carry forward indefinitely (no carryback)
- NOL deduction limited to 80% of taxable income
- Can offset up to 80% of future taxable income each year

### Planning Example

| Year | Rental Income | Deductions | NOL Used | NOL Remaining | Taxable | Tax (21%) |
|------|--------------|------------|----------|--------------|---------|-----------|
| 2025 | $50,086 | $185,000 | N/A | $105,932 | $0 | $0 |
| 2026 | $121,700 | $35,000 | $69,080 | $36,852 | $0 | $0 |
| 2027 | $121,700 | $35,000 | $36,852 | $0 | $49,848 | $10,468 |

**Strategy:** The created NOL shields all of 2025 tax (~$4,938) plus most of 2026.

---

## Phase 5: Tax Optimization Strategies

### 1. Related-Party Loan Interest

If the C-Corp is funded by a related-party loan (e.g., from parent company or shareholder):
- **Charge AFR interest rate** (Applicable Federal Rate ~4-5%)
- C-Corp deducts interest expense (reduces taxable income)
- Interest received by lender is taxable income (may be at lower rate)
- **Net benefit:** shifts income from 21% C-Corp rate to lender's rate

### 2. Management Fee Strategy

- C-Corp can pay management fees to a related management company
- Fees must be **reasonable** and for **actual services rendered**
- Document: bookkeeping, property oversight, tenant communications
- **Deductible at C-Corp level** (21% rate)

### 3. Retirement Plan Contributions

- C-Corp can establish a Solo 401(k) or SEP-IRA
- **Corporate contributions are tax-deductible**
- 2025 Solo 401(k) limit: $69,000 ($76,500 if age 50+)
- Requires earned income (salary) for employee side
- Corporate profit-sharing possible without salary

### 4. Section 179 Expensing

- Can expense up to $1,220,000 of qualifying property in 2025
- Phaseout begins at $3,050,000 of qualifying purchases
- Better than bonus depreciation for equipment under the phaseout threshold
- Qualifies: HVAC, fire suppression, security systems

### 5. De Minimis Safe Harbor Election

- Deduct items ≤ $2,500 per invoice immediately (not capitalize)
- Requires annual election on tax return
- Very useful for property maintenance items

### 6. Entity Structure Considerations

**C-Corp advantages:**
- 21% flat rate (vs individual 24-37%)
- Can retain earnings at 21% for future acquisitions
- More flexible fringe benefits

**S-Corp considerations:**
- Pass-through taxation eliminates double taxation
- Deadline: March 15 (late relief via Rev. Proc. 2013-30)
- QBI deduction generally not available for rental income
- Consult CPA before switching

### 7. Charitable Contributions (if applicable)

- C-Corps can deduct charitable contributions up to 10% of taxable income
- Requires taxable income to utilize (not useful if NOL)

---

## Phase 5: 1099-MISC Reconciliation for NNN Properties

### The Pass-Through Pattern (Critical Insight)

For NNN properties, **1099-MISC Box 1 commonly includes property tax proration** that the landlord pays to the county and the tenant reimburses. This is a **pass-through with net zero tax impact**:

- Tax reimbursement → income (included in gross rents on Form 1120 Line 5)
- Property tax paid → expense (deducted on Schedule A Line 5)
- **Net effect: $0 on taxable income**

This means even if the 1099 "over-reports" by including tax proration, **filing can proceed while awaiting payer confirmation**. The discrepancy is cosmetic, not financial.

### Reconciliation Workflow

1. Get 1099-MISC from payer
2. List all known payments: rent months, insurance reimb, HOA reimb, tax reimb
3. Calculate expected total = rent + reimbursements received in calendar year
4. Compare gap to property tax proration: total_tax / 12 × months_owned
5. If gap matches tax prorate → it's a pass-through, net zero impact
6. Email payer for itemized breakdown (good practice, NOT blocking)
7. File with 1099 amount (simplest) or actual income with explanatory statement

**Real-World Example: SKEstates Inc (sabithaandkrishnaestates)**
1099: $50,085.60 | Expected rent: $30,425.01 | Gap: ~$9,732 = ~4mo tax prorate ($29,195/12 × 4). Net zero impact. Filing proceeded while awaiting FD confirmation.

## Phase 6: Form 1120 Filing Plan Structure

When creating a filing plan doc for a C-Corp NNN property:

1. Entity Snapshot (EIN, address, incorporation, NAICS, bank)
2. Property Details (address, tenant, lease, rent, tax accounts)
3. Cost Basis (purchase + closing costs + §164(d) adj; land/building split)
4. Income (all calendar year receipts)
5. Deductions (Schedule A line-by-line)
6. Depreciation (Form 4562: cost seg vs standard, bonus rate)
7. Expected Tax Result (income - deductions; NOL projection)
8. Required Forms (1120, 8825, 4562, K, M-1)
9. E-Filing Options (service comparison with costs)
10. Filing Checklist (pre-filing through post-filing)
11. Key Dates (deadlines, reminders)
12. References (all supporting docs)

Save to `docs/tax/YEAR-filing-plan.md` in the entity repo.

## Phase 7: Texas Franchise Tax

### Overview

Texas has no state income tax but all entities registered with the TX Secretary of State must file a **franchise tax report** annually.

### Filing Details

| Item | Value |
|------|-------|
| Filing URL | comptroller.texas.gov/taxes/franchise/file-forms.php |
| Method | Webfile (online) |
| Deadline | May 15 (annual) |
| No-tax-due threshold | ~$2.47M total revenue |
| Penalty for not filing | $50/month, up to $200 |
| Risk | Business forfeiture after 2+ years of non-filing |

### Steps to File No-Tax-Due Report

1. Go to comptroller.texas.gov
2. Navigate to Franchise Tax → File Forms → Webfile
3. Need: EIN (39-2384131), Texas SOS file number
4. If first time filing, create a Webfile account
5. Select "No-Tax-Due Report" (revenue below threshold)
6. Enter total revenue from Form 1120
7. Submit electronically
8. **Save confirmation number**

---

## Phase 7: Direct E-Filing Options

### Federal Form 1120 E-Filing

| Service | 1120 Support | Cost (est) | E-File? | Notes |
|---------|-------------|-----------|---------|-------|
| IRS Free File | Select providers | Free | Yes | Check irs.gov/freefile |
| TurboTax Business | Yes | ~$200-300 | Yes | Most popular |
| TaxAct Business | Yes | ~$100-200 | Yes | Good value |
| FreeTaxUSA Business | Yes | ~$50-80 | Yes | Budget option |
| TaxSlayer | Limited | Varies | Varies | Check 1120 support |
| Drake Tax | Yes | ~$500+ | Yes | Pro software |
| Lacerte | Yes | ~$1,000+ | Yes | Pro tax suite |
| TaxWise | Yes | ~$500+ | Yes | Pro option |
| UltraTax CS | Yes | ~$1,000+ | Yes | Thomson Reuters |
| CCH Axcess | Yes | ~$1,000+ | Yes | Wolters Kluwer |

**For first-time filers with simple returns:** FreeTaxUSA or TaxAct are recommended (good cost-to-value for Form 1120 + 8825 + 4562).

### Paper Filing Alternative

If e-filing is not available or cost-prohibitive:
- Mail Form 1120 + all schedules + attachments
- Address: Department of the Treasury, Internal Revenue Service Center, Ogden, UT 84201-0012
- Include check for any tax due
- Certified mail recommended

### State E-Filing (Texas Franchise Tax)

- **Texas Comptroller Webfile** is the primary online filing method
- URL: comptroller.texas.gov/taxes/franchise/file-forms.php
- No-cost for No-Tax-Due reports

---

## Phase 8: 1099-MISC Reconciliation Protocol

### 1099-MISC Reconciliation Step-by-Step

**Step 1: Calculate expected income** — List what you know:
- Rent months × monthly rent = expected rent
- Reimbursements actually received in calendar year (insurance, HOA, etc.)
- Only payments **received in calendar year** count for that year's 1099

**Step 2: Calculate the gap** — 1099 Box 1 minus expected = gap.

**Step 3: Test common fillers for the gap:**
- Property tax proration (total annual tax ÷ 12 × months owned)
- Insurance reimbursement (full Crown/FDIC premium, not just property portion)
- HOA reimbursement
- Prior-year reimbursements included in same check

**Step 4: If gap matches a pass-through item, filing is NOT blocked.**
Property tax reimbursement is income AND expense — they offset. Same for any NNN cost you pay and get reimbursed for. Net taxable impact is $0.

**Step 5: Send clarification email to payer** (email template below) for official confirmation, but do not wait for a reply to file.

**Step 6: If gap is still unexplained and significant by filing deadline:**
- File with actual income (not 1099 amount)
- Attach statement explaining discrepancy
- Keep all correspondence on file

### Quick Gap Formula for NNN Mid-Year Acquisition

```
Expected 1099 = (Months of rent × monthly rent)
              + Insurance reimbursement received in calendar year
              + HOA reimbursement (if received)
              + Property tax proration (annual tax ÷ 12 × months owned)
```

If the reconstructed total is within ~$20 of the 1099, it's rounding. Move on.

### NNN Property Acquisition: Common Gap Explainer

When acquiring a NNN property mid-year, the 1099-MISC Box 1 often exceeds expected rent by including the **property tax proration**. Reconstruct the amount:

```
Expected 1099 = Rent months + Insurance reimb + HOA + Property tax proration
```

Example: Oct-Dec rent $30,425 + Insurance $9,519 + HOA $393 + Tax prorate $9,732 = $50,069 (vs 1099 $50,086, diff $17 rounding)

**Pass-through = net zero.** Property tax reimbursement is income, but property tax paid to county is an equal deduction. Net taxable impact is $0. **Filing is NOT blocked by a 1099-MISC amount that includes a tax prorate** — even if the exact proration math differs by ~$10-$20 due to rounding, the net result is identical either way.

---

## Pitfalls to Avoid

1. **Don't just report 1099 amount without reconciliation** — it may be wrong
2. **Don't mix calendar year and fiscal year** — 1099 reports calendar year
3. **Don't forget to count reimbursements as income** — they are taxable but offset by corresponding deductions
4. **Don't forget property tax proration at closing** — §164(d) allocation
5. **Don't forget Texas franchise tax** — still required even with zero tax due
6. **Don't miss Form 4562** — depreciation is the biggest deduction
7. **Don't ignore bonus depreciation phase-down** — 2025 = 40%, 2026 = 20%, 2027+ = 0%
8. **Don't commingle personal and corporate** — maintain separate accounts
9. **Watch related-party loan rules** — 0% interest loans may trigger imputed interest (AFR ~4-5%)
10. **Document self-prepared cost seg methodology** — critical for audit defense
11. **Don't skip the M-1 reconciliation** — required when income/assets > $250K
12. **Don't forget Form 8825** — required for C-Corp rental real estate

## Tax Research Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| IRS Forms & Pubs | irs.gov/forms-pubs | All tax forms, instructions, publications |
| IRC | law.cornell.edu/uscode/text/26 | Internal Revenue Code text |
| Pub 535 | irs.gov/pub/irs-pdf/p535.pdf | Business Expenses |
| Pub 542 | irs.gov/pub/irs-pdf/p542.pdf | Corporations |
| Pub 946 | irs.gov/pub/irs-pdf/p946.pdf | How to Depreciate Property |
| Pub 527 | irs.gov/pub/irs-pdf/p527.pdf | Residential Rental Property (NNN principles apply) |
| AFR Rates | irs.gov/applicable-federal-rates | Applicable Federal Rates for loans |
| TX Comptroller | comptroller.texas.gov | Texas franchise tax filing |
| Cost Seg Guide | irs.gov/irm/part04/irm_04-010-007 | IRS Audit Techniques Guide for Cost Segregation |
