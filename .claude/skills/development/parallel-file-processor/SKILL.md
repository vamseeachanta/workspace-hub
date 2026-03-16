---
name: parallel-file-processor
description: Process multiple files in parallel with aggregation and progress tracking.
  Use for batch file operations, directory scanning, ZIP handling, and parallel data
  processing with 2-3x performance improvement.
version: 1.1.0
category: development
related_skills:
- data-pipeline-processor
- yaml-workflow-executor
- engineering-report-generator
capabilities: []
requires: []
see_also:
- parallel-file-processor-core-pattern
- parallel-file-processor-core-components
- parallel-file-processor-basic-configuration
- parallel-file-processor-mode-selection
tags: []
---

# Parallel File Processor

## Quick Start

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd

def process_csv(file_path: Path) -> dict:
    """Process a single CSV file."""
    df = pd.read_csv(file_path)
    return {'file': file_path.name, 'rows': len(df), 'columns': len(df.columns)}

# Get all CSV files
files = list(Path('data/raw/').glob('*.csv'))

# Process in parallel
results = []
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(process_csv, f): f for f in files}
    for future in as_completed(futures):
        results.append(future.result())

print(f"Processed {len(results)} files")
```

## When to Use

- Processing large numbers of files (100+ files)
- Batch operations on directory contents
- Extracting data from multiple ZIP archives
- Aggregating results from parallel operations
- CPU-bound file transformations
- IO-bound file operations with proper concurrency

## Related Skills

- [data-pipeline-processor](../data-pipeline-processor/SKILL.md) - Data transformation
- [yaml-workflow-executor](../yaml-workflow-executor/SKILL.md) - Workflow automation
- [engineering-report-generator](../engineering-report-generator/SKILL.md) - Report generation

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format with Quick Start, Error Handling, Metrics, Execution Checklist, additional examples
- **1.0.0** (2024-10-15): Initial release with FileScanner, ParallelProcessor, progress tracking, result aggregation

## Sub-Skills

- [Example 1: Process CSV Files (+3)](example-1-process-csv-files/SKILL.md)
- [Do (+1)](do/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Metrics](metrics/SKILL.md)

## Sub-Skills

- [Core Pattern](core-pattern/SKILL.md)
- [Core Components (+5)](core-components/SKILL.md)
- [Basic Configuration](basic-configuration/SKILL.md)
- [Mode Selection (+2)](mode-selection/SKILL.md)
