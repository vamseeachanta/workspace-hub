---
name: bsee-sodir-extraction-1-bsee-data-extraction
description: 'Sub-skill of bsee-sodir-extraction: 1. BSEE Data Extraction.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 1. BSEE Data Extraction

## 1. BSEE Data Extraction


**Available datasets:**
- Production data (monthly oil/gas/water)
- Well data (API numbers, directional surveys)
- Platform/structure data
- Operator information
- Safety and incident data (OCS incidents)
- Environmental compliance

**Base URLs:**
```python
BSEE_BASE_URLS = {
    "production": "https://www.data.bsee.gov/Production/",
    "well": "https://www.data.bsee.gov/Well/",
    "platform": "https://www.data.bsee.gov/Platform/",
    "company": "https://www.data.bsee.gov/Company/",
    "field": "https://www.data.bsee.gov/Field/",
    "incidents": "https://www.data.bsee.gov/Incidents/",
}
```

**Production Data Extraction:**
```python
import pandas as pd
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional


def fetch_bsee_production_data(
    year: int,
    output_dir: Path,
    area_code: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch BSEE production data for a given year.

    Args:
        year: Production year (e.g., 2024)
        output_dir: Directory to save downloaded data
        area_code: Optional area filter ('GC', 'MC', 'WR', etc.)

    Returns:
        DataFrame with production data
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # BSEE provides production data as downloadable files
    url = f"https://www.data.bsee.gov/Production/Files/ogoraan{year}.zip"

    # Download file
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    zip_path = output_dir / f"production_{year}.zip"
    with open(zip_path, "wb") as f:
        f.write(response.content)

    # Extract and read
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(output_dir)

    # Read the extracted CSV
    csv_files = list(output_dir.glob(f"*{year}*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV found for {year}")

    df = pd.read_csv(csv_files[0])

    # Filter by area if specified
    if area_code:
        df = df[df["AREA_CODE"] == area_code]

    # Clean column names
    df.columns = df.columns.str.strip().str.upper()

    # Add metadata
    df["EXTRACTION_DATE"] = datetime.now().isoformat()
    df["SOURCE"] = "BSEE"

    print(f"Fetched {len(df)} production records for {year}")

    return df


def aggregate_production_by_field(
    df: pd.DataFrame,
    time_period: str = "monthly"
) -> pd.DataFrame:
    """
    Aggregate production data by field.

    Args:
        df: Raw production DataFrame
        time_period: 'monthly', 'quarterly', or 'annual'

    Returns:
        Aggregated production DataFrame
    """
    # Group by field
    group_cols = ["FIELD_NAME", "AREA_CODE", "BLOCK_NUMBER"]

    if time_period == "monthly":
        group_cols.extend(["PRODUCTION_YEAR", "PRODUCTION_MONTH"])
    elif time_period == "quarterly":
        df["QUARTER"] = ((df["PRODUCTION_MONTH"] - 1) // 3) + 1
        group_cols.extend(["PRODUCTION_YEAR", "QUARTER"])
    else:  # annual
        group_cols.append("PRODUCTION_YEAR")

    # Aggregate
    agg_dict = {
        "OIL_BBL": "sum",
        "GAS_MCF": "sum",
        "WATER_BBL": "sum",
        "WELL_COUNT": "nunique" if "API_NUMBER" in df.columns else "count"
    }

    # Only aggregate columns that exist
    agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}

    aggregated = df.groupby(group_cols).agg(agg_dict).reset_index()

    return aggregated


# Example usage
production_2024 = fetch_bsee_production_data(
    year=2024,
    output_dir=Path("data/raw/bsee"),
    area_code="GC"  # Green Canyon
)

field_production = aggregate_production_by_field(
    production_2024,
    time_period="monthly"
)

print(field_production.head())
```

**Well Data Extraction:**
```python
def fetch_bsee_well_data(
    api_number: Optional[str] = None,
    field_name: Optional[str] = None,
    output_dir: Path = Path("data/raw/bsee")
) -> pd.DataFrame:
    """
    Fetch BSEE well data.

    Args:
        api_number: Specific API number (14-digit)
        field_name: Filter by field name
        output_dir: Output directory

    Returns:
        DataFrame with well data
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # BSEE Well File download
    url = "https://www.data.bsee.gov/Well/Files/Well.zip"

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    zip_path = output_dir / "well_data.zip"
    with open(zip_path, "wb") as f:
        f.write(response.content)

    import zipfile
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(output_dir)

    # Read well data
    well_file = output_dir / "Well.csv"
    df = pd.read_csv(well_file)

    # Filter if specified
    if api_number:
        df = df[df["API_WELL_NUMBER"] == api_number]
    if field_name:

*Content truncated — see parent skill for full reference.*
