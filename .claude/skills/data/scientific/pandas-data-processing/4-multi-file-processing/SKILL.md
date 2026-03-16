---
name: pandas-data-processing-4-multi-file-processing
description: 'Sub-skill of pandas-data-processing: 4. Multi-File Processing.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 4. Multi-File Processing

## 4. Multi-File Processing


**Batch CSV Loading:**
```python
def load_multiple_csv_files(
    directory: Path,
    pattern: str = '*.csv',
    concat_axis: int = 0
) -> pd.DataFrame:
    """
    Load and concatenate multiple CSV files.

    Args:
        directory: Directory containing CSV files
        pattern: Glob pattern for file matching
        concat_axis: Concatenation axis (0=rows, 1=columns)

    Returns:
        Concatenated DataFrame
    """
    csv_files = sorted(directory.glob(pattern))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found matching {pattern} in {directory}")

    # Load all files
    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df['source_file'] = csv_file.name  # Track source
        dfs.append(df)

    # Concatenate
    combined = pd.concat(dfs, axis=concat_axis, ignore_index=True)

    print(f"Loaded {len(csv_files)} files, total {len(combined)} rows")

    return combined

# Example: Load all mooring tension results
all_tensions = load_multiple_csv_files(
    Path('data/processed/mooring_tensions/'),
    pattern='tension_line*.csv'
)

print(f"Combined dataset: {all_tensions.shape}")
```

**Multi-Format Data Loading:**
```python
def load_engineering_data(
    file_path: Path,
    file_type: str = None
) -> pd.DataFrame:
    """
    Load data from multiple engineering file formats.

    Args:
        file_path: Path to data file
        file_type: File type ('csv', 'excel', 'hdf5', 'parquet', 'json')
                   If None, inferred from extension

    Returns:
        Loaded DataFrame
    """
    if file_type is None:
        file_type = file_path.suffix.lstrip('.')

    # Load based on type
    if file_type == 'csv':
        df = pd.read_csv(file_path)
    elif file_type in ['xls', 'xlsx', 'excel']:
        df = pd.read_excel(file_path)
    elif file_type in ['h5', 'hdf5']:
        df = pd.read_hdf(file_path)
    elif file_type == 'parquet':
        df = pd.read_parquet(file_path)
    elif file_type == 'json':
        df = pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    print(f"Loaded {file_type.upper()}: {df.shape[0]} rows, {df.shape[1]} columns")

    return df

# Usage examples
csv_data = load_engineering_data(Path('data/processed/results.csv'))
excel_data = load_engineering_data(Path('data/processed/summary.xlsx'))
hdf5_data = load_engineering_data(Path('data/processed/large_dataset.h5'))
```
