# Cost Segregation Analysis — NNN Commercial Property

## What is Cost Segregation?

A cost segregation study is an engineering-based tax analysis that reclassifies
components of a building from 39-year structural life into shorter-lived asset
categories (5, 7, or 15 years). Shorter lives qualify for accelerated depreciation
and bonus depreciation, dramatically front-loading tax deductions.

IRS authority: Rev. Proc. 87-56, Rev. Proc. 2011-26, IRS Audit Techniques Guide
(Cost Segregation, 2004).

---

## Component Classification Framework

| Component Category | MACRS Life | Examples | Typical % of Building |
|-------------------|-----------|---------|----------------------|
| Structure | 39 years | Walls, roof, foundation, structural framing, load-bearing elements | 65-75% |
| Land improvements | 15 years | Parking lot, landscaping, drainage, exterior signage, fencing, sidewalks | 15-20% |
| Personal property (5-yr) | 5 years | Carpeting, specialized lighting, decorative fixtures, counters | 5-10% |
| Personal property (7-yr) | 7 years | Tenant-specific electrical, dedicated HVAC units, security systems, specialty flooring | 5-10% |

### Retail NNN Benchmarks (Conservative)
For a single-tenant retail store (Dollar General, Family Dollar, Dollar Tree, CVS, Walgreens):
- Structure: 70-75% (use 75% conservative)
- Land improvements: 15% (parking, drive, landscaping)
- Personal property: 10% (electrical, HVAC, flooring, fixtures)
- Total reclassification: 25-30% of building basis

---

## Bonus Depreciation Phase-Down Schedule (TCJA §168(k))

Components with 5, 7, or 15-year lives qualify for bonus depreciation (first-year
expensing of a portion of the basis). The TCJA set 100% bonus starting 2017,
phasing down annually:

| Placed in Service Year | Bonus Rate |
|----------------------|-----------|
| 2022 | 100% |
| 2023 | 80% |
| 2024 | 60% |
| 2025 | 40% |
| 2026 | 20% |
| 2027+ | 0% |

Bonus depreciation applies BEFORE regular MACRS. Remaining basis after bonus
is recovered under regular MACRS over the asset life.

---

## SKEstates Inc 2025 Calculation

Building basis: $1,089,534 | Placed in service: September 2025 | Bonus rate: 40%

| Component | Basis | Life | Bonus (40%) | MACRS Year 1 | Total Year 1 |
|-----------|-------|------|------------|--------------|-------------|
| Structure (75%) | $817,151 | 39 yr | None | $6,120 (0.749%) | $6,120 |
| Land improvements (15%) | $163,430 | 15 yr | $65,372 | $8,172 | $73,544 |
| Personal property (10%) | $108,953 | 5-7 yr | $43,581 | $9,360 | $52,942 |
| TOTAL | $1,089,534 | -- | $108,953 | $23,652 | $132,606 |

Standard depreciation Year 1: $8,161
Cost segregation Year 1: $132,606
Additional Year 1 deduction: $124,445

### Tax Impact (21% C-Corp Rate)
| Scenario | Taxable Income | Federal Tax |
|---------|--------------|------------|
| Standard depreciation | $23,513 | $4,938 |
| Cost segregation | -$105,932 (NOL) | $0 |

---

## Self-Prepared vs. Professional Study

### Self-Prepared (Acceptable for Simple Properties)
- Appropriate for: single-tenant retail NNN, well-documented component percentages
- Use published IRS/industry benchmarks (conservative end of range)
- Prepare a written methodology document citing IRS authority
- Document: property description, component breakdown, percentages used, IRS citations
- Defensibility threshold: ≤30% reclassification for single-tenant retail

### Professional Study ($3,000-$7,000 typical)
- Required for: complex properties, high-value basis, aggressive reclassification
- Provides "qualified written report" -- highest audit protection
- Cost is itself deductible in year paid
- ROI: breakeven at ~$15K-35K additional depreciation (depending on tax rate)

### Documentation Requirements (Both Methods)
1. Property acquisition date and basis allocation (HUD statement)
2. Written description of each reclassified component
3. Benchmark percentages cited with source (IRS ATG, industry publications)
4. Clear separation of land, building, and improvements on closing docs
5. Any photos or blueprints supporting the allocation

---

## Depreciation Recapture on Sale

When a property with accelerated depreciation is sold:
- §1250 recapture: unrecaptured straight-line equivalent gain taxed at max 25%
- All depreciation claimed reduces basis for gain calculation
- Cost segregation benefit = TIME VALUE of early deductions vs. larger recapture later

### Hold Period Analysis
| Hold Period | Cost Seg Benefit |
|------------|-----------------|
| <3 years | Often negative (recapture exceeds NPV of early deductions) |
| 3-5 years | Break-even to modest benefit |
| 5+ years | Clear benefit (time value of deferred tax exceeds recapture cost) |
| 10+ years | Maximum benefit; recapture may be at lower rate than avoided tax rate |

---

## IRS Audit Considerations

- Cost segregation is a targeted audit area; IRS has specific audit techniques guide
- Self-prepared studies without documentation are the highest audit risk
- Conservative benchmarks + written methodology = strong defensible position
- IRS has accepted self-prepared studies for routine commercial properties
- Auditors look for: reasonable percentages, consistent methodology, written support
- Red flags: >35% reclassification on simple property, no written study, inconsistent treatment year-over-year

---

## References

- IRS Audit Techniques Guide: Cost Segregation (2004, updated 2022)
- Rev. Proc. 87-56 -- MACRS asset classes and recovery periods
- IRC §168 -- Accelerated Cost Recovery System (ACRS/MACRS)
- IRC §168(k) -- Bonus depreciation (TCJA §13201)
- IRS Publication 946 -- How to Depreciate Property
- IRC §1250 -- Depreciation recapture on real property
