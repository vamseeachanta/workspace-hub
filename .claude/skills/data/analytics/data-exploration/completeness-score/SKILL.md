---
name: data-exploration-completeness-score
description: 'Sub-skill of data-exploration: Completeness Score (+3).'
version: 1.0.0
category: data-analytics
type: reference
scripts_exempt: true
---

# Completeness Score (+3)

## Completeness Score


Rate each column:
- **Complete** (>99% non-null): Green
- **Mostly complete** (95-99%): Yellow -- investigate the nulls
- **Incomplete** (80-95%): Orange -- understand why and whether it matters
- **Sparse** (<80%): Red -- may not be usable without imputation


## Consistency Checks


Look for:
- **Value format inconsistency**: Same concept represented differently ("USA", "US", "United States", "us")
- **Type inconsistency**: Numbers stored as strings, dates in various formats
- **Referential integrity**: Foreign keys that don't match any parent record
- **Business rule violations**: Negative quantities, end dates before start dates, percentages > 100
- **Cross-column consistency**: Status = "completed" but completed_at is null


## Accuracy Indicators


Red flags that suggest accuracy issues:
- **Placeholder values**: 0, -1, 999999, "N/A", "TBD", "test", "xxx"
- **Default values**: Suspiciously high frequency of a single value
- **Stale data**: Updated_at shows no recent changes in an active system
- **Impossible values**: Ages > 150, dates in the far future, negative durations
- **Round number bias**: All values ending in 0 or 5 (suggests estimation, not measurement)


## Timeliness Assessment


- When was the table last updated?
- What is the expected update frequency?
- Is there a lag between event time and load time?
- Are there gaps in the time series?
