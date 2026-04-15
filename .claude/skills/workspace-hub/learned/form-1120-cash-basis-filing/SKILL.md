---
name: form-1120-cash-basis-filing
description: Complete Form 1120 preparation for C-Corp cash-basis filers — includes TaxAct Business Online interview flow for Schedule L, M-1, M-2
version: 2.0.0
source: auto-extracted + session-learned
extracted: 2026-04-15
metadata:
  tags: ["tax", "form-1120", "c-corp", "cash-basis", "corporate-tax", "taxact"]
---

# Form 1120 Cash-Basis Filing

When preparing Form 1120 for a cash-method C-Corp, use the expense sheet (bank-activity view) as authoritative source of truth for revenue and expenses. Map each expense line to corresponding Form 1120 line items, then coordinate Schedule J, L, K, M-1, M-2. FreeTaxUSA does not support Form 1120; use TaxAct Business Online, IRS PDF, or PdfFiller.

## TaxAct Business Online — Interview Flow

TaxAct uses a guided interview format. The sidebar sections are:
About the Business > Officers > Federal (Income, Deductions, Credits, Miscellaneous, Summary) > State > Review > Filing

### Schedule L, M-1, M-2 (under Federal > Miscellaneous)

#### Balance Sheet - Assets (3+ pages)
1. **Page 1**: Cash, Trade notes/accounts receivable, Inventories, U.S. government obligations
2. **Page 2**: Tax-exempt securities, Loans to shareholders, Mortgage/real estate loans, Buildings/depreciable assets, Accumulated depreciation
3. **Page 3**: Depletable assets, Accumulated depletion, Land (net of amortization), Intangible assets
4. **Other Current Assets**: Freeform description + BOY/EOY
5. **Other Investments**: Freeform description + BOY/EOY
6. **Other Assets**: Freeform description + BOY/EOY

#### Balance Sheet - Liabilities (3 pages)
7. **Liabilities**: Accounts payable, Mortgages/notes/bonds < 1yr, Loans from shareholders, Mortgages/notes/bonds >= 1yr
8. **Current Liabilities**: Freeform description + BOY/EOY — use for "Federal income tax payable"
9. **Other Liabilities**: Freeform description + BOY/EOY

#### Balance Sheet - Stockholder Equity (1 page)
10. Preferred stock, Common stock, Additional paid-in capital, Retained earnings appropriated, Adjustments to shareholder equity, Cost of treasury stock

**CRITICAL**: "Retained earnings unappropriated" (Schedule L Line 24) is NOT shown on this page. TaxAct auto-computes it from Schedule M-2 ending balance.

#### Schedule M-1 — Reconciliation (7 pages + overview)
11. Federal income tax expense on books (Line 2)
12. Excess of capital losses over capital gains (Line 3)
13. Income on tax return not in books (Line 4)
14. Expenses in books not on return — depreciation (Line 5a)
15. Expenses in books not on return — itemized list (Line 5b): accrued fees, vacation/bonus, bad debt, amortization, fines, goodwill, life insurance premiums, prepaid, reserves, state tax, asset sale loss
16. Income in books not on return (Line 7): tax-exempt interest, asset sale gain, installment sales, life insurance proceeds, unearned revenue, other
17. Depreciation on return not in books (Line 8a)
18. Other deductions on return not in books (Line 8b): same itemized categories

**KEY**: M-1 Line 10 = Page 1 Line 28 (taxable income BEFORE NOL). Do NOT include NOL deduction on M-1 Line 8. NOL is a Line 29a deduction, separate from M-1 reconciliation.

19. **Reconciliation Overview**: verify Line 10 = Page 1 Line 28

#### Schedule M-2 — Retained Earnings (5 pages + overview)
20. Beginning of year balance (from prior year M-2 Line 8 or reconstructed)
21. Other additions (freeform description + amount)
22. Distributions: cash / stock / property
23. Other reductions (freeform description + amount)
24. **M-2 Overview**: ending balance = BOY + net income + additions - distributions - reductions

#### Miscellaneous Topics (checkbox page)
25. Estimated Tax Penalty (Form 2220) — **select this if prior year tax was $0 to claim safe harbor**
26. Alternative Minimum Tax (Form 4626) — only for $1B+ corporations
27. Excise tax on stock repurchase (Form 7208)
28. Foreign ownership reporting
29. S-Corp election (Form 2553)
30. 2026 Estimated Tax worksheet

## TaxAct Pitfalls

1. **Excessive whitespace** — pages have huge blank areas. Use browser `find` tool to locate buttons rather than scrolling.
2. **RE unappropriated missing** — TaxAct does NOT show a field for Schedule L Line 24. It auto-computes from M-2 ending balance. Fill M-2 first.
3. **Estimated tax penalty** — TaxAct auto-calculates a penalty if you skip Form 2220. Select the checkbox to enter prior year tax = $0 for safe harbor.
4. **Federal Owed in header** — includes TaxAct's filing fee (~$55), so the displayed amount is higher than actual tax.
5. **Line 26 Other Deductions** — no generic "Other" field. Map expenses to TaxAct's predefined categories (Professional dues, Contracted services, Janitorial, Utilities, Telephone, Office expenses).
6. **Balance sheet won't balance** until M-2 is completed and RE unappropriated auto-populates.

## Cross-Check Verification

| Check | Formula |
|-------|---------|
| Schedule L balance | Total assets = Total L&E (both BOY and EOY) |
| M-1 reconciliation | Line 10 = Page 1 Line 28 (pre-NOL) |
| M-2 → Schedule L | M-2 ending balance = Schedule L Line 24 (RE unappropriated EOY) |
| Tax computation | Taxable income x 21% = Tax (Schedule J) |
| Page 1 flow | Line 11 - Line 27 = Line 28 |
| NOL limit | 80% of Line 28 under TCJA |
