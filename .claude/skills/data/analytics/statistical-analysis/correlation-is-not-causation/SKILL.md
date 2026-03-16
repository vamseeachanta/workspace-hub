---
name: statistical-analysis-correlation-is-not-causation
description: 'Sub-skill of statistical-analysis: Correlation Is Not Causation (+5).'
version: 1.0.0
category: data-analytics
type: reference
scripts_exempt: true
---

# Correlation Is Not Causation (+5)

## Correlation Is Not Causation


When you find a correlation, explicitly consider:
- **Reverse causation**: Maybe B causes A, not A causes B
- **Confounding variables**: Maybe C causes both A and B
- **Coincidence**: With enough variables, spurious correlations are inevitable

**What you can say**: "Users who use feature X have 30% higher retention"
**What you cannot say without more evidence**: "Feature X causes 30% higher retention"


## Multiple Comparisons Problem


When you test many hypotheses, some will be "significant" by chance:
- Testing 20 metrics at p=0.05 means ~1 will be falsely significant
- If you looked at many segments before finding one that's different, note that
- Adjust for multiple comparisons with Bonferroni correction (divide alpha by number of tests) or report how many tests were run


## Simpson's Paradox


A trend in aggregated data can reverse when data is segmented:
- Always check whether the conclusion holds across key segments
- Example: Overall conversion goes up, but conversion goes down in every segment -- because the mix shifted toward a higher-converting segment


## Survivorship Bias


You can only analyze entities that "survived" to be in your dataset:
- Analyzing active users ignores those who churned
- Analyzing successful companies ignores those that failed
- Always ask: "Who is missing from this dataset, and would their inclusion change the conclusion?"


## Ecological Fallacy


Aggregate trends may not apply to individuals:
- "Countries with higher X have higher Y" does NOT mean "individuals with higher X have higher Y"
- Be careful about applying group-level findings to individual cases


## Anchoring on Specific Numbers


Be wary of false precision:
- "Churn will be 4.73% next quarter" implies more certainty than is warranted
- Prefer ranges: "We expect churn between 4-6% based on historical patterns"
- Round appropriately: "About 5%" is often more honest than "4.73%"
