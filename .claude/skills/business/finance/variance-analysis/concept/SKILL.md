---
name: variance-analysis-concept
description: 'Sub-skill of variance-analysis: Concept (+4).'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Concept (+4)

## Concept


A waterfall (or bridge) chart shows how you get from one value to another through a series of positive and negative contributors. Used to visualize variance decomposition.


## Data Structure


```
Starting value:  [Base/Budget/Prior period amount]
Drivers:         [List of contributing factors with signed amounts]
Ending value:    [Actual/Current period amount]

Verification:    Starting value + Sum of all drivers = Ending value
```


## Text-Based Waterfall Format


When a charting tool is not available, present as a text waterfall:

```
WATERFALL: Revenue — Q4 Actual vs Q4 Budget

Q4 Budget Revenue                                    $10,000K
  |
  |--[+] Volume growth (new customers)               +$800K
  |--[+] Expansion revenue (existing customers)      +$400K
  |--[-] Price reductions / discounting               -$200K
  |--[-] Churn / contraction                          -$350K
  |--[+] FX tailwind                                  +$50K
  |--[-] Timing (deals slipped to Q1)                 -$150K
  |
Q4 Actual Revenue                                    $10,550K

Net Variance: +$550K (+5.5% favorable)
```


## Bridge Reconciliation Table


Complement the waterfall with a reconciliation table:

| Driver | Amount | % of Variance | Cumulative |
|--------|--------|---------------|------------|
| Volume growth | +$800K | 145% | +$800K |
| Expansion revenue | +$400K | 73% | +$1,200K |
| Price reductions | -$200K | -36% | +$1,000K |
| Churn / contraction | -$350K | -64% | +$650K |
| FX tailwind | +$50K | 9% | +$700K |
| Timing (deal slippage) | -$150K | -27% | +$550K |
| **Total variance** | **+$550K** | **100%** | |

*Note: Percentages can exceed 100% for individual drivers when there are offsetting items.*


## Waterfall Best Practices


1. Order drivers from largest positive to largest negative (or in logical business sequence)
2. Keep to 5-8 drivers maximum — aggregate smaller items into "Other"
3. Verify the waterfall reconciles (start + drivers = end)
4. Color-code: green for favorable, red for unfavorable (in visual charts)
5. Label each bar with both the amount and a brief description
6. Include a "Total Variance" summary bar
