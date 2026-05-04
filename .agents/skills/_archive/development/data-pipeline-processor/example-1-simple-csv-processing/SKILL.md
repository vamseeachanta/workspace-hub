---
name: data-pipeline-processor-example-1-simple-csv-processing
description: 'Sub-skill of data-pipeline-processor: Example 1: Simple CSV Processing
  (+3).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Simple CSV Processing (+3)

## Example 1: Simple CSV Processing


```bash
# Process CSV with config
python -m data_pipeline config/pipelines/clean_data.yaml

# Override input/output
python -m data_pipeline config/pipelines/clean_data.yaml \
    --input data/custom_input.csv \
    --output data/custom_output.csv

# Dry run (validate only)
python -m data_pipeline config/pipelines/clean_data.yaml --dry-run
```


## Example 2: Programmatic Usage


```python
from data_pipeline import DataPipeline, PipelineConfig

config = PipelineConfig(
    input_path='data/raw/sales.csv',
    output_path='data/processed/sales_clean.csv',
    validation={
        'required_columns': ['date', 'product', 'amount'],
        'non_null_columns': ['amount']
    },
    transformations=[
        {'operation': 'filter', 'expression': 'amount > 0'},
        {'operation': 'sort', 'by': ['date']}
    ]
)

pipeline = DataPipeline(config)
result = pipeline.run()
print(f"Processed {result['output_rows']} rows")
```


## Example 3: Batch Processing


```python
from pathlib import Path
from data_pipeline import DataReader, DataTransformer, DataExporter

reader = DataReader()
exporter = DataExporter()

# Process all CSV files in directory
input_dir = Path('data/raw/')
output_dir = Path('data/processed/')

for csv_file in input_dir.glob('*.csv'):
    df = reader.read(str(csv_file))

    # Apply transformations
    df_clean = (DataTransformer(df)
        .fill_nulls(value=0)
        .filter_rows('value > 0')
        .sort(['timestamp'])
        .get_result())

    # Export
    output_path = output_dir / csv_file.name
    exporter.to_csv(df_clean, str(output_path))
    print(f"Processed: {csv_file.name}")
```


## Example 4: Multi-Format Export


```python
def export_all_formats(df: pd.DataFrame, base_path: str):
    """Export data to multiple formats."""
    exporter = DataExporter()

    outputs = {
        'csv': exporter.to_csv(df, f"{base_path}.csv"),
        'json': exporter.to_json(df, f"{base_path}.json"),
        'parquet': exporter.to_parquet(df, f"{base_path}.parquet"),
        'excel': exporter.to_excel(df, f"{base_path}.xlsx")
    }

    return outputs
```
