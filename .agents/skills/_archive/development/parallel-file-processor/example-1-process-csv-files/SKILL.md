---
name: parallel-file-processor-example-1-process-csv-files
description: 'Sub-skill of parallel-file-processor: Example 1: Process CSV Files (+3).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Process CSV Files (+3)

## Example 1: Process CSV Files


```python
from parallel_file_processor import (
    FileScanner, FileProcessor, ProcessingMode,
    ProgressTracker, ResultAggregator
)
from pathlib import Path
import pandas as pd

# Define processing function
def process_csv(file_info):
    """Extract statistics from CSV file."""
    df = pd.read_csv(file_info.path)
    return {
        'rows': len(df),
        'columns': len(df.columns),
        'memory_mb': df.memory_usage(deep=True).sum() / 1e6,
        'numeric_columns': len(df.select_dtypes(include='number').columns)
    }

# Setup scanner and processor
scanner = FileScanner(extensions={'.csv'})
processor = FileProcessor(
    scanner=scanner,
    mode=ProcessingMode.THREAD_POOL,
    max_workers=8
)

# Create progress tracker
tracker = ProgressTracker(0, "Processing CSVs")
tracker.start()

# Process with progress
result = processor.process_directory(
    Path("data/raw/"),
    process_csv,
    progress_callback=tracker.update
)

tracker.finish()

# Aggregate results
aggregator = ResultAggregator(result)
print(f"\nSummary: {aggregator.summary()}")
aggregator.export_csv(Path("data/results/csv_stats.csv"))
```


## Example 2: Parallel ZIP Extraction


```python
# Extract all ZIPs in parallel
processor = FileProcessor(mode=ProcessingMode.THREAD_POOL)

result = processor.extract_all_zips(
    directory=Path("data/archives/"),
    output_directory=Path("data/extracted/")
)

print(f"Extracted {result.successful} ZIP files")
print(f"Failed: {result.failed}")

# Get extraction details
aggregator = ResultAggregator(result)
df = aggregator.to_dataframe()
total_files = df['result_files_extracted'].sum()
print(f"Total files extracted: {total_files}")
```


## Example 3: Aggregate Data from Multiple Sources


```python
# Aggregate CSV files with custom processing
def load_and_clean(file_info):
    """Load CSV and perform basic cleaning."""
    df = pd.read_csv(file_info.path)

    # Clean column names
    df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]

    # Add metadata
    df['_source'] = file_info.path.name
    df['_loaded_at'] = pd.Timestamp.now()

    return df

processor = FileProcessor(
    scanner=FileScanner(extensions={'.csv'}),
    mode=ProcessingMode.THREAD_POOL
)

result = processor.process_directory(
    Path("data/monthly_reports/"),
    load_and_clean
)

# Combine all DataFrames
aggregator = ResultAggregator(result)
combined_df = aggregator.combine_dataframes()

print(f"Combined {len(combined_df)} rows from {result.successful} files")
combined_df.to_csv("data/combined_reports.csv", index=False)
```


## Example 4: Custom Batch Processing


```python
from parallel_file_processor import ParallelProcessor, ProcessingMode

# Process list of items (not files)
items = list(range(1000))

def heavy_computation(item):
    """CPU-intensive calculation."""
    import math
    result = sum(math.sin(i * item) for i in range(10000))
    return {'item': item, 'result': result}

# Use process pool for CPU-bound work
processor = ParallelProcessor(
    processor=heavy_computation,
    mode=ProcessingMode.PROCESS_POOL,
    max_workers=4
)

# Track progress
def show_progress(completed, total):
    pct = (completed / total) * 100
    print(f"\rProgress: {pct:.1f}%", end='', flush=True)

processor.on_progress(show_progress)

result = processor.process(items)
print(f"\nCompleted {result.successful}/{result.total_files} items")
```
