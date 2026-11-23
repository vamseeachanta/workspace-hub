---
name: yaml-workflow-executor
description: Execute data processing workflows defined in YAML configuration files. Supports data loading, transformation, validation, and reporting pipelines.
version: 1.0.0
category: workspace-hub
type: skill
trigger: manual
auto_execute: false
capabilities:
  - yaml_configuration
  - pipeline_execution
  - data_processing
  - workflow_orchestration
  - bash_integration
tools:
  - Read
  - Write
  - Bash
related_skills:
  - python-project-template
  - interactive-report-generator
  - data-validation-reporter
---

# YAML Workflow Executor

> Execute standardized data processing workflows from YAML configuration files.

## Quick Start

```bash
# Execute workflow from YAML
/yaml-workflow-executor config/input/analysis.yaml

# Execute with output directory
/yaml-workflow-executor config/input/pipeline.yaml --output reports/

# Dry run (validate only)
/yaml-workflow-executor config/input/pipeline.yaml --dry-run
```

## When to Use

**USE when:**
- Running standardized analysis workflows
- Batch processing with different parameters
- Creating reproducible pipelines
- Separating configuration from code

**DON'T USE when:**
- One-off scripts
- Interactive exploration
- Configuration is simple (single parameter)

## Prerequisites

- Python 3.9+
- pyyaml>=6.0
- pydantic>=2.0 (for validation)
- Data files in expected locations

## Overview

Implements the YAML → Script → Report pattern used across workspace-hub:

1. **Load YAML** - Parse configuration file
2. **Validate** - Check required fields and types
3. **Execute** - Run processing pipeline
4. **Report** - Generate output and logs

## YAML Configuration Format

### Standard Structure

```yaml
# config/input/analysis_pipeline.yaml

# Metadata (required)
metadata:
  name: "data-analysis-pipeline"
  version: "1.0.0"
  created: "2026-01-14"
  author: "analyst"
  description: "Process and analyze CSV data"

# Input configuration
input:
  source:
    type: "csv"                    # csv, excel, json, parquet
    path: "data/raw/input.csv"     # Relative path
    encoding: "utf-8"

  validation:
    required_columns: ["id", "value", "date"]
    max_rows: 1000000
    max_size_mb: 100

# Processing steps
processing:
  steps:
    - name: "clean_data"
      operation: "remove_nulls"
      columns: ["value"]

    - name: "transform"
      operation: "calculate"
      expression: "value * 1.1"
      output_column: "adjusted_value"

    - name: "aggregate"
      operation: "group_by"
      by: ["category"]
      aggregations:
        value: "sum"
        count: "count"

# Output configuration
output:
  format: "html"                   # html, csv, json, excel
  path: "reports/analysis_report.html"
  include_plots: true
  plots:
    - type: "time_series"
      x: "date"
      y: ["value", "adjusted_value"]
    - type: "bar"
      x: "category"
      y: "sum_value"

# Execution settings
execution:
  log_level: "INFO"
  parallel: false
  timeout_minutes: 30
```

### Complete Example

```yaml
# config/input/bsee_analysis.yaml
metadata:
  name: "bsee-production-analysis"
  version: "2.0.0"
  created: "2026-01-14"
  author: "energy-analyst"
  description: "BSEE production data analysis with NPV calculation"

input:
  source:
    type: "csv"
    path: "data/raw/bsee_production.csv"
    date_columns: ["production_date"]
    parse_dates: true

  filters:
    - column: "field_name"
      operator: "in"
      values: ["JULIA", "ANCHOR", "JACK"]
    - column: "production_date"
      operator: ">="
      value: "2020-01-01"

  validation:
    required_columns:
      - "api_number"
      - "field_name"
      - "oil_bbl"
      - "gas_mcf"
      - "production_date"
    numeric_columns: ["oil_bbl", "gas_mcf", "water_bbl"]

processing:
  steps:
    - name: "clean"
      operation: "fillna"
      columns: ["water_bbl"]
      value: 0

    - name: "calculate_boe"
      operation: "add_column"
      expression: "oil_bbl + gas_mcf / 6"
      output_column: "boe"

    - name: "monthly_aggregate"
      operation: "resample"
      date_column: "production_date"
      frequency: "M"
      aggregations:
        oil_bbl: "sum"
        gas_mcf: "sum"
        boe: "sum"

    - name: "npv_calculation"
      operation: "npv"
      cash_flow_column: "revenue"
      discount_rates: [0.08, 0.10, 0.12]
      periods: 20

output:
  format: "html"
  path: "reports/bsee_analysis_{timestamp}.html"
  title: "BSEE Production Analysis"

  summary:
    include: true
    metrics:
      - "total_oil_bbl"
      - "total_gas_mcf"
      - "total_boe"
      - "npv_results"

  plots:
    - type: "time_series"
      title: "Monthly Production"
      x: "production_date"
      y: ["oil_bbl", "gas_mcf"]

    - type: "bar"
      title: "Production by Field"
      x: "field_name"
      y: "total_boe"

    - type: "line"
      title: "NPV Sensitivity"
      x: "discount_rate"
      y: "npv"

execution:
  log_level: "INFO"
  save_intermediate: true
  intermediate_path: "data/processed/"
  parallel: true
  n_workers: 4
```

## Core Implementation

### Workflow Executor Class

```python
"""
ABOUTME: YAML workflow executor for standardized data pipelines
ABOUTME: Executes configuration-driven processing workflows
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from pydantic import BaseModel, validator


class InputConfig(BaseModel):
    """Input configuration model."""
    type: str = "csv"
    path: str
    encoding: str = "utf-8"
    date_columns: List[str] = []
    parse_dates: bool = True


class ProcessingStep(BaseModel):
    """Processing step configuration."""
    name: str
    operation: str
    columns: Optional[List[str]] = None
    expression: Optional[str] = None
    output_column: Optional[str] = None


class WorkflowConfig(BaseModel):
    """Complete workflow configuration."""
    metadata: Dict[str, Any]
    input: Dict[str, Any]
    processing: Dict[str, Any]
    output: Dict[str, Any]
    execution: Dict[str, Any] = {}


class YAMLWorkflowExecutor:
    """Execute workflows defined in YAML configuration."""

    def __init__(self, config_path: Path):
        """
        Initialize executor with configuration file.

        Args:
            config_path: Path to YAML configuration
        """
        self.config_path = Path(config_path)
        self.config: Optional[WorkflowConfig] = None
        self.data: Optional[pd.DataFrame] = None
        self.results: Dict[str, Any] = {}

        self._setup_logging()
        self._load_config()

    def _setup_logging(self):
        """Configure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self):
        """Load and validate configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with open(self.config_path) as f:
            raw_config = yaml.safe_load(f)

        self.config = WorkflowConfig(**raw_config)
        self.logger.info(f"Loaded config: {self.config.metadata.get('name')}")

    def validate(self) -> bool:
        """
        Validate configuration without executing.

        Returns:
            True if valid, False otherwise
        """
        errors = []

        # Check input file exists
        input_path = Path(self.config.input['source']['path'])
        if not input_path.exists():
            errors.append(f"Input file not found: {input_path}")

        # Check output directory
        output_path = Path(self.config.output['path']).parent
        if not output_path.exists():
            self.logger.warning(f"Output directory will be created: {output_path}")

        # Validate processing steps
        for step in self.config.processing.get('steps', []):
            if 'name' not in step:
                errors.append("Processing step missing 'name'")
            if 'operation' not in step:
                errors.append(f"Step '{step.get('name')}' missing 'operation'")

        if errors:
            for error in errors:
                self.logger.error(error)
            return False

        self.logger.info("Configuration validated successfully")
        return True

    def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute the workflow.

        Args:
            dry_run: If True, validate without executing

        Returns:
            Results dictionary
        """
        if dry_run:
            self.validate()
            return {"status": "dry_run", "valid": True}

        start_time = datetime.now()
        self.logger.info(f"Starting workflow: {self.config.metadata.get('name')}")

        try:
            # Step 1: Load data
            self._load_data()

            # Step 2: Execute processing steps
            self._execute_processing()

            # Step 3: Generate output
            self._generate_output()

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            self.results['status'] = 'success'
            self.results['execution_time'] = execution_time
            self.logger.info(f"Workflow completed in {execution_time:.2f}s")

        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            self.results['status'] = 'failed'
            self.results['error'] = str(e)
            raise

        return self.results

    def _load_data(self):
        """Load input data based on configuration."""
        source = self.config.input['source']
        path = Path(source['path'])
        file_type = source.get('type', 'csv')

        self.logger.info(f"Loading data from: {path}")

        if file_type == 'csv':
            self.data = pd.read_csv(
                path,
                encoding=source.get('encoding', 'utf-8'),
                parse_dates=source.get('date_columns', [])
            )
        elif file_type == 'excel':
            self.data = pd.read_excel(path)
        elif file_type == 'parquet':
            self.data = pd.read_parquet(path)
        elif file_type == 'json':
            self.data = pd.read_json(path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        self.logger.info(f"Loaded {len(self.data)} rows")
        self.results['input_rows'] = len(self.data)

    def _execute_processing(self):
        """Execute processing steps."""
        steps = self.config.processing.get('steps', [])

        for i, step in enumerate(steps):
            self.logger.info(f"Step {i+1}/{len(steps)}: {step['name']}")
            self._execute_step(step)

        self.results['output_rows'] = len(self.data)

    def _execute_step(self, step: Dict[str, Any]):
        """Execute a single processing step."""
        operation = step['operation']

        if operation == 'remove_nulls':
            columns = step.get('columns', self.data.columns.tolist())
            self.data = self.data.dropna(subset=columns)

        elif operation == 'fillna':
            columns = step.get('columns', self.data.columns.tolist())
            value = step.get('value', 0)
            self.data[columns] = self.data[columns].fillna(value)

        elif operation == 'calculate':
            expression = step['expression']
            output_col = step['output_column']
            self.data[output_col] = self.data.eval(expression)

        elif operation == 'add_column':
            expression = step['expression']
            output_col = step['output_column']
            self.data[output_col] = self.data.eval(expression)

        elif operation == 'group_by':
            by = step['by']
            aggs = step['aggregations']
            self.data = self.data.groupby(by).agg(aggs).reset_index()

        elif operation == 'filter':
            column = step['column']
            op = step['operator']
            value = step['value']

            if op == '==':
                self.data = self.data[self.data[column] == value]
            elif op == '>':
                self.data = self.data[self.data[column] > value]
            elif op == '>=':
                self.data = self.data[self.data[column] >= value]
            elif op == 'in':
                self.data = self.data[self.data[column].isin(value)]

        elif operation == 'resample':
            date_col = step['date_column']
            freq = step['frequency']
            aggs = step['aggregations']
            self.data = self.data.set_index(date_col).resample(freq).agg(aggs).reset_index()

        else:
            self.logger.warning(f"Unknown operation: {operation}")

    def _generate_output(self):
        """Generate output based on configuration."""
        output = self.config.output
        format_type = output.get('format', 'csv')

        # Handle timestamp in path
        path_str = output['path']
        if '{timestamp}' in path_str:
            path_str = path_str.replace(
                '{timestamp}',
                datetime.now().strftime('%Y%m%d_%H%M%S')
            )

        output_path = Path(path_str)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format_type == 'csv':
            self.data.to_csv(output_path, index=False)
        elif format_type == 'excel':
            self.data.to_excel(output_path, index=False)
        elif format_type == 'parquet':
            self.data.to_parquet(output_path, index=False)
        elif format_type == 'html':
            self._generate_html_report(output_path, output)
        elif format_type == 'json':
            self.data.to_json(output_path, orient='records', indent=2)

        self.logger.info(f"Output saved: {output_path}")
        self.results['output_path'] = str(output_path)

    def _generate_html_report(self, output_path: Path, config: Dict[str, Any]):
        """Generate interactive HTML report."""
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        title = config.get('title', 'Analysis Report')

        # Create figure with subplots for each configured plot
        plots = config.get('plots', [])

        if plots:
            fig = make_subplots(
                rows=len(plots),
                cols=1,
                subplot_titles=[p.get('title', f'Plot {i+1}') for i, p in enumerate(plots)]
            )

            for i, plot_config in enumerate(plots):
                plot_type = plot_config['type']

                if plot_type == 'time_series' or plot_type == 'line':
                    for y_col in plot_config['y']:
                        fig.add_trace(
                            go.Scatter(
                                x=self.data[plot_config['x']],
                                y=self.data[y_col],
                                name=y_col,
                                mode='lines'
                            ),
                            row=i+1, col=1
                        )

                elif plot_type == 'bar':
                    fig.add_trace(
                        go.Bar(
                            x=self.data[plot_config['x']],
                            y=self.data[plot_config['y']],
                            name=plot_config['y']
                        ),
                        row=i+1, col=1
                    )

            fig.update_layout(height=400 * len(plots), title_text=title)
            fig.write_html(output_path, include_plotlyjs='cdn')
        else:
            # Simple data table export
            self.data.to_html(output_path)


def run_workflow(config_path: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Run workflow from configuration file.

    Args:
        config_path: Path to YAML configuration
        dry_run: If True, validate only

    Returns:
        Results dictionary
    """
    executor = YAMLWorkflowExecutor(Path(config_path))
    return executor.execute(dry_run=dry_run)
```

### Bash Wrapper Script

```bash
#!/bin/bash
# scripts/run_workflow.sh
# Execute YAML-configured workflow

set -e

CONFIG_FILE="$1"
OUTPUT_DIR="${2:-./reports}"
DRY_RUN="${3:-false}"

if [ -z "$CONFIG_FILE" ]; then
    echo "Usage: ./scripts/run_workflow.sh <config.yaml> [output_dir] [--dry-run]"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "=========================================="
echo "YAML Workflow Executor"
echo "Config: $CONFIG_FILE"
echo "Output: $OUTPUT_DIR"
echo "=========================================="

# Activate UV environment if available
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Execute workflow
if [ "$DRY_RUN" = "--dry-run" ] || [ "$DRY_RUN" = "true" ]; then
    python -c "
from workflow_executor import run_workflow
result = run_workflow('$CONFIG_FILE', dry_run=True)
print(f'Validation: {result}')
"
else
    python -c "
from workflow_executor import run_workflow
result = run_workflow('$CONFIG_FILE')
print(f'Result: {result}')
"
fi

echo "Workflow complete!"
```

## Usage Examples

### Example 1: Basic Data Processing

```yaml
# config/input/basic_processing.yaml
metadata:
  name: "basic-processing"
  version: "1.0.0"

input:
  source:
    type: "csv"
    path: "data/raw/input.csv"

processing:
  steps:
    - name: "remove_nulls"
      operation: "remove_nulls"
      columns: ["value"]

    - name: "add_calculated"
      operation: "calculate"
      expression: "value * 2"
      output_column: "doubled_value"

output:
  format: "csv"
  path: "data/processed/output.csv"
```

```bash
# Execute
./scripts/run_workflow.sh config/input/basic_processing.yaml
```

### Example 2: Analysis with Report

```yaml
# config/input/analysis_with_report.yaml
metadata:
  name: "analysis-report"
  version: "1.0.0"

input:
  source:
    type: "csv"
    path: "data/raw/sales_data.csv"
    date_columns: ["sale_date"]

processing:
  steps:
    - name: "filter_recent"
      operation: "filter"
      column: "sale_date"
      operator: ">="
      value: "2025-01-01"

    - name: "aggregate_monthly"
      operation: "group_by"
      by: ["product_category"]
      aggregations:
        revenue: "sum"
        quantity: "sum"

output:
  format: "html"
  path: "reports/sales_analysis.html"
  title: "Sales Analysis Report"
  plots:
    - type: "bar"
      title: "Revenue by Category"
      x: "product_category"
      y: "revenue"
```

## Execution Checklist

**Configuration:**
- [ ] YAML file is valid syntax
- [ ] Input path exists
- [ ] Required columns specified
- [ ] Processing steps are ordered

**Execution:**
- [ ] Run dry-run first (`--dry-run`)
- [ ] Check input data quality
- [ ] Monitor execution logs
- [ ] Verify output generated

**Validation:**
- [ ] Output file created
- [ ] Row counts match expectations
- [ ] Plots render correctly
- [ ] No error messages

## Error Handling

### Config Not Found
```
Error: Config not found: config/input/missing.yaml

Check:
1. File path is correct
2. File exists
3. Correct working directory
```

### Invalid YAML
```
Error: YAML parsing failed

Check:
1. Valid YAML syntax
2. No tabs (use spaces)
3. Correct indentation
```

### Missing Input
```
Error: Input file not found: data/raw/input.csv

Check:
1. Input path is relative to project root
2. File has been downloaded/created
3. Path separators correct for OS
```

## Best Practices

1. **Use version control** for config files
2. **Start with dry-run** to validate
3. **Use timestamps** in output paths for history
4. **Document configs** with comments
5. **Test incrementally** - add steps one at a time

## Related Skills

- [python-project-template](../python-project-template/SKILL.md) - Project setup
- [interactive-report-generator](../interactive-report-generator/SKILL.md) - Report generation
- [data-validation-reporter](../data-validation-reporter/SKILL.md) - Data quality

## References

- [YAML 1.2 Specification](https://yaml.org/spec/1.2.2/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [workspace-hub Development Workflow](../../../docs/modules/workflow/DEVELOPMENT_WORKFLOW.md)

---

## Version History

- **1.0.0** (2026-01-14): Initial release - YAML-configured workflow executor with data processing, validation, and HTML report generation
