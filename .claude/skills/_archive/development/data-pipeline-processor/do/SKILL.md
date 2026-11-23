---
name: data-pipeline-processor-do
description: 'Sub-skill of data-pipeline-processor: Do (+6).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Do (+6)

## Do


1. Always detect encoding before reading CSV
2. Use chunked reading for large files (>100MB)
3. Specify dtypes to reduce memory usage
4. Handle missing values explicitly
5. Validate early in the pipeline
6. Fail fast on critical errors
7. Log warnings for non-critical issues
8. Track validation statistics


## Don't


1. Assume encoding is always UTF-8
2. Load entire large files into memory
3. Skip validation steps
4. Ignore encoding errors
5. Mix transformation and validation


## Data Reading

- Always detect encoding before reading CSV
- Use chunked reading for large files (>100MB)
- Specify dtypes to reduce memory usage
- Handle missing values explicitly


## Validation

- Validate early in the pipeline
- Fail fast on critical errors
- Log warnings for non-critical issues
- Track validation statistics


## Transformation

- Use method chaining for readability
- Apply filters before expensive operations
- Convert types early to catch errors
- Document transformation logic


## Export

- Create output directories automatically
- Use appropriate formats (Parquet for large data)
- Include metadata in output
- Verify output integrity


## File Organization

```
project/
    config/
        pipelines/           # Pipeline configs
            clean_data.yaml
            aggregate.yaml
    data/
        raw/                 # Raw input data
        processed/           # Cleaned data
        results/             # Analysis results
    src/
        data_pipeline/       # Pipeline code
    scripts/
        run_pipeline.sh      # CLI wrapper
```
