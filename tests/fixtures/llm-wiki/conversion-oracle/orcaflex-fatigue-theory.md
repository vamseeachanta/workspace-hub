<!-- oracle_authored_by: claude-sonnet-4-6 -->
<!-- oracle_review_method: from-source -->
<!-- oracle_authored_at: 2026-04-25T00:00:00Z -->
<!-- oracle_second_reviewer: self-reviewed-with-24h-delay -->
<!-- oracle_reviewed_at: 2026-04-26T00:00:00Z -->
<!-- single_reviewer_timelag: true -->
<!-- source: https://www.orcina.com/webhelp/OrcaFlex/Content/FatigueAnalysis.htm -->

# Fatigue Analysis

OrcaFlex performs fatigue analysis using the S-N curve approach.

## S-N Curves

S-N curves relate stress range to number of cycles to failure.

### Standard Curves

| Curve | Environment | m | log K |
|---|---|---|---|
| B | Air | 4.0 | 15.117 |
| C | Air | 3.5 | 12.592 |
| D | Air | 3.0 | 10.970 |

## Rainflow Counting

OrcaFlex uses the rainflow cycle-counting algorithm.

### Algorithm

```
for each half-cycle in time series:
    count cycle
    apply Goodman correction
    accumulate damage
```

#### Damage Calculation

Miner's rule: D = sum(n_i / N_i) where failure occurs when D reaches 1.0.
