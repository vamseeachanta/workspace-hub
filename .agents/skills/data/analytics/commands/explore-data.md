---
name: explore-data
type: command
plugin: data
source: https://github.com/anthropics/knowledge-work-plugins
---

# /explore-data - Profile a Dataset

Generate a detailed profile of a table or uploaded file to reveal shape, quality, and patterns before analysis.

## Usage

```
/explore-data <table_name or file>
```

## Workflow

### 1. Access the Data

If a data warehouse MCP server is connected:
- Look up the table schema
- Pull sample data and compute profiling statistics via SQL

If the user uploads a file:
- Load the file (CSV, Excel, Parquet, JSON)
- Inspect the structure

### 2. Structural Overview

Compute and report:
- Row count and column count
- Data types for each column
- Date range (min/max for temporal columns)
- Primary key candidate identification

### 3. Column-Level Profiling

For each column, compute:
- Null count and null rate
- Distinct count and cardinality ratio
- Most/least common values with frequencies
- Type-specific statistics (percentiles for numeric, lengths for string, distribution for dates)

### 4. Quality Flags

Identify and flag:
- High null rates: Columns with >5% nulls (warn), >20% nulls (alert)
- Suspicious values: Placeholder values, impossible ranges
- Duplicate detection: Potential duplicate rows or near-duplicate records
- Consistency issues: Mixed formats, type mismatches

### 5. Recommendations

Based on the profile, suggest:
- **Dimensions to slice by**: Categorical columns suitable for segmentation
- **Metrics to measure**: Numeric columns suitable for aggregation
- **Follow-up analyses**: 3-5 specific analyses suited to this dataset's characteristics

## Output Structure

1. **Overview**: Table summary with row/column counts, date range, grain
2. **Column Details**: Table with column name, type, nulls, cardinality, top values, stats
3. **Quality Issues**: Flagged concerns with severity
4. **Exploration Suggestions**: Recommended next steps

## Performance Notes

- For large tables (100M+ rows), use sampling for profiling
- Compute approximate percentiles and distinct counts where exact computation is too expensive
