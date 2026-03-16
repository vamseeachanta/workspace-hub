---
name: data-pipeline-processor
description: Process data files through transformation pipelines with validation,
  cleaning, and export. Use for CSV/Excel/JSON data processing, encoding handling,
  batch operations, and data transformation workflows.
version: 1.1.0
category: development
related_skills:
- yaml-workflow-executor
- engineering-report-generator
- parallel-file-processor
capabilities: []
requires: []
see_also:
- data-pipeline-processor-error-handling
- data-pipeline-processor-execution-checklist
- data-pipeline-processor-metrics
tags: []
---

# Data Pipeline Processor

## Quick Start

```python
import pandas as pd
from pathlib import Path

# Simple pipeline: Load -> Transform -> Export
df = pd.read_csv("data/raw/source.csv")

# Transform
df = df[df['value'] > 0]  # Filter
df['date'] = pd.to_datetime(df['date'])  # Convert types
df = df.sort_values('date')  # Sort

# Export
Path("data/processed").mkdir(parents=True, exist_ok=True)
df.to_csv("data/processed/cleaned.csv", index=False)

print(f"Processed {len(df)} rows")
```

## When to Use

- Processing CSV/Excel/JSON files with validation
- Data cleaning and transformation workflows
- Batch file processing with aggregation
- Handling encoding issues (UTF-8, Latin-1 fallback)
- ETL (Extract, Transform, Load) operations
- Data quality checks and reporting

## Core Pattern

```
Input (CSV/Excel/JSON) -> Validate -> Transform -> Analyze -> Export
```

## Implementation

### Data Reader with Encoding Detection

```python
import pandas as pd
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
import chardet

logger = logging.getLogger(__name__)



*See sub-skills for full details.*
### Data Validator

```python
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)

*See sub-skills for full details.*
### Data Transformer

```python
class DataTransformer:
    """Apply transformations to data."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def rename_columns(self, mapping: Dict[str, str]) -> 'DataTransformer':
        """Rename columns."""
        self.df = self.df.rename(columns=mapping)

*See sub-skills for full details.*
### Data Exporter

```python
class DataExporter:
    """Export data to various formats."""

    @staticmethod
    def to_csv(df: pd.DataFrame, path: str, **kwargs) -> str:
        """Export to CSV."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False, **kwargs)
        return path

*See sub-skills for full details.*
### Pipeline Orchestrator

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class PipelineConfig:
    """Configuration for data pipeline."""
    input_path: str
    output_path: str

*See sub-skills for full details.*

## YAML Configuration Format

### Basic Pipeline Config

```yaml
# config/pipelines/data_clean.yaml

input:
  path: data/raw/source.csv
  options:
    delimiter: ","
    skiprows: 1

validation:

*See sub-skills for full details.*
### Aggregation Pipeline

```yaml
# config/pipelines/monthly_summary.yaml

input:
  path: data/processed/daily_data.csv

validation:
  required_columns:
    - date
    - category

*See sub-skills for full details.*

## Related Skills

- [yaml-workflow-executor](../yaml-workflow-executor/SKILL.md) - Workflow orchestration
- [engineering-report-generator](../engineering-report-generator/SKILL.md) - Report generation
- [parallel-file-processor](../parallel-file-processor/SKILL.md) - Parallel file operations

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format with Quick Start, Error Handling, Metrics, Execution Checklist, additional examples
- **1.0.0** (2024-10-15): Initial release with DataReader, DataValidator, DataTransformer, pipeline orchestration

## Sub-Skills

- [Example 1: Simple CSV Processing (+3)](example-1-simple-csv-processing/SKILL.md)
- [Do (+6)](do/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Metrics](metrics/SKILL.md)
