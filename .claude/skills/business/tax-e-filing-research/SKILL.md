---
name: tax-e-filing-research
description: Guide to directly e-filing federal Form 1120 and state franchise tax returns. Covers service comparison, cost analysis, step-by-step filing procedures, and paper filing alternatives for C-Corp entities.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [tax, e-file, Form-1120, Form-8825, Texas, franchise-tax, filing]
metadata:
  hermes:
    tags: [tax, e-file, Form-1120, Texas, franchise-tax]
---

# Tax E-Filing Research — Form 1120 + State Returns

Comprehensive guide to directly filing corporate federal and state tax returns without a CPA.

## When to Use This Skill

- Preparing to e-file Form 1120 independently
- Comparing e-filing service options for cost and features
- Need step-by-step filing instructions
- Paper filing backup plan

---

## Federal Form 1120 E-Filing Options

### Budget Options ($50-$150)

| Service | 1120 Support | Forms Available | E-File Cost | State Support |
|---------|-------------|----------------|-------------|--------------|
| **FreeTaxUSA Business** | **Recommended** | 1120, 8825, 4562, Schedule K, M-1 | Free federal, ~$15 state | TX franchise tax supported |
| TaxAct Business | Yes | 1120, 8825, 4562, all schedules | ~$60 federal | TX supported |
| H&R Block Business | Limited | 1120, 8825, 4562 | ~$100-150 | TX supported |

### Professional Options ($200-$1000+)

| Service | 1120 Support | Features | E-File Cost |
|---------|-------------|----------|-------------|
| TurboTax Business | Full | Guided interview, all schedules | ~$200-300 |
| Drake Tax | Full | Pro-grade, all forms, multi-state | ~$500+ |
| Lacerte (Intuit Pro) | Full | Enterprise-grade | ~$1,000+ |
| CCH Axcess (Wolters Kluwer) | Full | Enterprise-grade, multi-firm | ~$1,000+ |
| UltraTax CS (Thomson Reuters) | Full | Enterprise-grade | ~$1,000+ |

**Recommendation for SKEstates Inc:** For a first-time filer with a simple NNN property return, **FreeTaxUSA Business** or **TaxAct Business** are the best value. Both support Form 1120, 8825, 4562, Schedule K, and M-1 reconciliation.

---

## Step-by-Step: Form 1120 Filing Process

### Preparation (Before E-File)

1. **Gather all documents:**
   - EIN confirmation letter (CP 575 or 147C)
   - Form 1099-MISC from Family Dollar
   - Bank statements for all months
   - Property purchase documents (HUD Settlement Statement)
   - Property tax bills and receipts
   - Insurance premium invoices
   - HOA fee invoices
   - Cost segregation analysis

2. **Calculate key numbers:**
   - Total rental income (actual deposits, not just 1099)
   - Total deductions (property tax, insurance, HOA, management, depreciation)
   - Net income or NOL
   - Depreciation (Form 4562)

### Form 1120 Line Items for NNN Property

| Line | Description | Typical Value |
|------|-------------|---------------|
| 1a | Gross receipts/sales | 0 |
| 2 | Cost of goods sold | 0 |
| 3 | Dividends | 0 |
| 4 | Interest | 0 |
| 5 | Gross rents | Monthly rent + reimb |
| 6 | Other income | 0 |
| 7 | Total income | Line 5 |
| **Deductions:** | | |
| 5 | Taxes and licenses | Property taxes |
| 8 | Depreciation | From Form 4562 |
| 9 | Depletion | 0 |
| 10 | Advertising | 0 |
| 11 | Pension/profit-sharing | 0 |
| 12 | Employee benefit programs | 0 |
| 13 | Other deductions | Insurance + HOA + mgmt + prof fees |

### Additional Required Forms

**Form 8825 (Rental Real Estate Income and Expenses):**
- Part I, Line 1a: Gross rents
- Part I, Line 3: Royalties (if applicable)
- Part I, Lines 4-19: Expenses (taxes, insurance, repairs, mgmt, etc.)
- Part I, Line 20: Depreciation (from 4562)
- Part I, Line 21: Total expenses
- Part I, Line 22: Net income or loss

**Form 4562 (Depreciation and Amortization):**
- Part I: Election to expense certain depreciable property (§179)
- Part II: Special Depreciation Allowance (bonus depreciation)
- Part III: MACRS Depreciation (building, land improvements)
- Part VI: Short-term/long-term property

---

## Texas Franchise Tax Filing

### No-Tax-Due Report

**Steps:**
1. Go to comptroller.texas.gov
2. Select "Franchise Tax" → "File Forms Online"
3. Click "Webfile"
4. Log in or create account (first-time requires creation)
5. Select "No-Tax-Due Report"
6. Enter:
   - EIN: 39-2384131
   - Total Revenue (from Form 1120, Line 1a through 6)
   - Entity type: Corporation
7. Review and submit
8. Save confirmation number

**Required Information:**
- EIN
- Texas SOS File Number
- Total Revenue from Form 1120
- Accounting method (same as federal return)

### If Revenue Exceeds Threshold (~$2.47M)

- Must calculate margin tax
- May need to file Form 05-102 (Franchise Tax Report)
- Tax rate: 0.75% (most entities) or 0.375% (retail/wholesale)
- No-tax-due report still recommended as backup

---

## Paper Filing Backup

### Federal Form 1120 (Mail)

**Where to Mail:**
- Department of the Treasury
- Internal Revenue Service Center
- Ogden, UT 84201

**What to Include:**
- Form 1120 (all pages)
- Schedule K
- Schedule M-1 (if required)
- Form 8825
- Form 4562
- Any supporting schedules
- Check for tax due (if any)
- Copy of 1099-MISC (if different from reported income, include explanatory statement)

**Recommended:** Send via Certified Mail, Return Receipt Requested

### Texas Franchise Tax (Mail)

- Texas Comptroller of Public Accounts
- P.O. Box 13528
- Austin, TX 78711-3528

- Use Form 05-102 (Franchise Tax Report)
- Mark "No Tax Due" if applicable

---

## E-Filing vs Paper Filing

| Factor | E-File | Paper Mail |
|--------|--------|-----------|
| Speed | 24-72 hours for IRS receipt | 4-8 weeks |
| Confirmation | Immediate electronic | Certified mail receipt |
| Accuracy | Built-in validation | Manual review |
| Cost | $0-300 (software) | $0 (just postage) |
| Convenience | Fill online | Print and mail |
| Error rate | Lower | Higher |
| Amendments | Easier | Must re-file |

**Recommendation:** E-file whenever possible. The built-in validation and immediate confirmation are worth the small cost for peace of mind and audit trail.

---

## Common Filing Errors to Avoid

1. **Wrong EIN or entity name** — must match IRS records exactly
2. **Missing Form 8825** — required for all rental real estate income
3. **Depreciation errors** — most common error on NNN returns
4. **Not reporting reimbursements** — they are taxable income
5. **Wrong tax year** — first-year short period (May 27 to Dec 31, 2025 for SKEstates)
6. **Missing M-1** — required when total assets or gross receipts > $250,000
7. **Not signing** — must be signed by authorized officer
8. **Not including state filing** — TX franchise tax due May 15
