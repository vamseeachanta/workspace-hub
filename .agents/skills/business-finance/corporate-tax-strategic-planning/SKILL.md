---
name: corporate-tax-strategic-planning
version: "1.0.0"
category: business-finance
description: "Reverse-engineer target tax outcomes, model multi-year retained earnings and R&D funding, and produce strategic tax analysis for small C-Corps. Covers deduction gap analysis, capital source modeling, §174 R&D amortization timing, NOL carryforward projections, and loan structure optimization."
tags: [tax, c-corp, strategic-planning, r&d, reverse-engineering, retained-earnings, nol, section-174, funding-model]
type: reference
---

# Corporate Tax Strategic Planning

Reverse-engineer target tax outcomes, model multi-year funding for R&D,
and produce strategic tax analysis for small C-Corps with consulting revenue.

## When to Use

- User wants to reduce corporate tax to a specific target (reverse engineering)
- User wants to model retained earnings + R&D budget across multiple years
- User asks about funding future growth from current-year earnings
- User wants to evaluate tax impact of different spending strategies
- User asks about loan structuring between related entities

## Phase 1: Reverse-Engineer Target Tax to Required Deductions

### Step 1: Calculate the gap

```
Target tax / 0.21 = Required taxable income
Revenue - Required taxable income = Required total deductions
Required deductions - Current documented deductions = Gap
```

### Step 2: List every possible deduction category

For each category note:
- Maximum gap it can fill
- Current amount (if any)
- Documentation status (have, need, impossible)
- IRS risk level

Categories to check:
1. Officer/W-2 compensation (retroactive = impossible for prior years)
2. Subcontractor/contractor costs (check all bank statements)
3. R&D expenses (§162 vs §174 classification)
4. Equipment/hardware (IRC §179)
5. Professional services (legal, accounting, consulting)
6. Insurance premiums
7. Travel/client expenses (50% deductible for meals)
8. Home office (simplified vs actual method)
9. Software/cloud compute
10. Interest expense
11. Bad debt
12. Advertising/marketing
13. Education/training

### Step 3: Sum realistic additional deductions

Total realistic gap fill = sum of categories with actual documentation or
high probability of bank statement confirmation.

### Step 4: Calculate achievable minimum tax

```
Revenue - (current + realistic additional deductions) = Achievable taxable income
Achievable taxable income x 0.21 = Achievable tax
```

### Critical Insight
If the gap is >50% of revenue, flag it as unrealistic. A normal consulting
firm has 40-60% direct labor/COGS. >90% total expense ratio = red flag.

## Phase 2: Retained Earnings and Multi-Year Funding Model

### Step 1: Baseline current retained cash

```
Revenue - Expenses - Tax = Retained earnings
```

### Step 2: Identify all capital sources
- Retained earnings from current year
- Existing loans (remaining balance)
- Loan-to-equity conversion possibility
- Personal capital injection
- Revenue from operations
- External funding

### Step 3: Model section 174 R&D amortization timing

Post-2022, R&D is NOT fully deductible in Year 1:
- Domestic: 5-year amortization, half-year convention
- Year 1: 10% of R&D (R / 5 / 2)
- Year 2-5: 20% per year
- Year 6: 10% (remaining half)

This means a $300K R&D spend creates only $30K in Year 1 deductions.
The remaining $270K is a section 174 amortization pool that provides deductions
in future years.

### Step 4: Project 5-year cash flow AND tax

For each year model:
- Cash in bank (beginning balance + income - spending)
- Tax deductions (current-year expenses + section 174 amortization + operating)
- NOL created (if deductions > revenue)
- Cumulative NOL balance
- Future section 174 pool remaining

### Step 5: NOL utilization plan

When revenue resumes:
- NOL offsets up to 80% of taxable income per year
- Calculate years to consume full NOL
- Model tax liability during and after NOL period

## Phase 3: Loan Structure Analysis

### Multi-entity loan chain mapping

```
Entity A (personal) -> Entity B (operating) -> Entity C (investment)
```

For each link evaluate:
1. Imputed interest (IRC section 7872) - 0% loans trigger phantom income
2. Balance sheet impact - receivable/payable bloat
3. Audit complexity - IRS tracing funds through entities
4. Cash flow impact - repayments draining operating cash
5. Tax advantage (usually none for pass-through between related entities)

### Restructuring evaluation
- Direct route (eliminate middleman entity)
- Loan-to-equity conversion
- Loan forgiveness (triggers CODI = taxable!)
- Interest rate change to AFR

**CRITICAL:** Loan forgiveness = cancellation of debt income (CODI) = taxable to debtor. Loan conversion to equity is NOT taxable.

## Phase 4: Document Everything

### Output files (in the entity repo)

```
taxes/2025/
├── 2025-corporate-tax-analysis.yaml          # 3+ scenarios, all numbers
├── 2025-ai-rd-budget-strategy.yaml           # R&D thesis, QRE classification
├── 2025-retained-earnings-ai-growth-model.yaml  # 5-yr funding model
└── session-tax-review-YYYY-MM-DD.md           # Session summary
```

Each YAML file should be self-contained - usable by future sessions.

## Pitfalls

1. **Confusing spending with deduction** - Money spent on assets (section 179) stays
   in the company as an asset, the cost is deducted. This is the ONLY way
   to both retain value AND deduct the cost.

2. **Assuming R&D is fully deductible** - section 174 amortization since 2022
   means only 10% is deductible in Year 1.

3. **Loan forgiveness as tax strategy** - CODI makes forgiven debt taxable
   income. Conversion to equity is not taxable.

4. **Retroactive W-2** - Cannot issue a W-2 for a prior tax year after
   that year has ended. Only possible prospectively.

5. **NOL carryforward assumptions** - Must confirm prior year returns were
   filed. If 2024 is unfiled, the 2023 NOL is unsubstantiated.

6. **Itemizing vs standard** - For TX (no state tax), property tax alone
   rarely exceeds the MFJ standard deduction ($31,500 in 2025). Always compare.

## GitHub Issue Pattern

When creating future tax/strategy issues:

| Priority | When       | Pattern                                    |
|----------|-----------|--------------------------------------------|
| BLOCKER  | ASAP      | Unfiled prior year returns                 |
| HIGH     | Quarter   | Missing docs, extension decisions            |
| MEDIUM   | Next year | Annual filing with year header (2027, 2028...) |
| LOW      | Future    | Strategic planning (R&D, productization)    |

Close issues when they are:
- Captured in documentation (use "exit strategy" issue)
- Superseded by a better approach
- Premature (future actions with no current-year relevance)
- Not actionable (loans that are only retrospective internal documentation)
