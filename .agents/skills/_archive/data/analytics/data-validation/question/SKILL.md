---
name: data-validation-question
description: 'Sub-skill of data-validation: Question (+9).'
version: 1.0.0
category: data-analytics
type: reference
scripts_exempt: true
---

# Question (+9)

## Question

[The specific question being answered]


## Data Sources

- Table: [schema.table_name] (as of [date])
- Table: [schema.other_table] (as of [date])
- File: [filename] (source: [where it came from])


## Definitions

- [Metric A]: [Exactly how it's calculated]
- [Segment X]: [Exactly how membership is determined]
- [Time period]: [Start date] to [end date], [timezone]


## Methodology

1. [Step 1 of the analysis approach]
2. [Step 2]
3. [Step 3]


## Assumptions and Limitations

- [Assumption 1 and why it's reasonable]
- [Limitation 1 and its potential impact on conclusions]


## Key Findings

1. [Finding 1 with supporting evidence]
2. [Finding 2 with supporting evidence]


## SQL Queries

[All queries used, with comments]


## Caveats

- [Things the reader should know before acting on this]
```


## Code Documentation


For any code (SQL, Python) that may be reused:

```python
"""
Analysis: Monthly Cohort Retention
Author: [Name]
Date: [Date]
Data Source: events table, users table
Last Validated: [Date] -- results matched dashboard within 2%

Purpose:
    Calculate monthly user retention cohorts based on first activity date.

Assumptions:
    - "Active" means at least one event in the month
    - Excludes test/internal accounts (user_type != 'internal')
    - Uses UTC dates throughout

Output:
    Cohort retention matrix with cohort_month rows and months_since_signup columns.
    Values are retention rates (0-100%).
"""
```


## Version Control for Analyses


- Save queries and code in version control (git) or a shared docs system
- Note the date of the data snapshot used
- If an analysis is re-run with updated data, document what changed and why
- Link to prior versions of recurring analyses for trend comparison
