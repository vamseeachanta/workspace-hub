---
name: bsee-sodir-extraction-2-sodirnpd-data-extraction-norway
description: 'Sub-skill of bsee-sodir-extraction: 2. SODIR/NPD Data Extraction (Norway).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 2. SODIR/NPD Data Extraction (Norway)

## 2. SODIR/NPD Data Extraction (Norway)


**Available datasets:**
- Field production (oil, gas, NGL, condensate)
- Well data (exploration, development)
- Discoveries and prospects
- Company information
- Pipeline and infrastructure

**FactPages API:**
```python
import requests
import pandas as pd
from typing import Dict, List, Optional


class SODIRDataFetcher:
    """Fetch data from SODIR (Norwegian Offshore Directorate) FactPages."""

    BASE_URL = "https://factpages.sodir.no/api/v1"

    ENDPOINTS = {
        "fields": "/fields",
        "field_production": "/field-production-yearly",
        "wells": "/wells",
        "discoveries": "/discoveries",
        "companies": "/companies",
        "pipelines": "/pipelines",
        "facilities": "/facilities",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "EnergyDataAnalysis/1.0"
        })

    def _fetch(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch data from SODIR API."""
        url = f"{self.BASE_URL}{endpoint}"

        response = self.session.get(url, params=params, timeout=60)
        response.raise_for_status()

        return response.json()

    def get_all_fields(self) -> pd.DataFrame:
        """Get all Norwegian offshore fields."""
        data = self._fetch(self.ENDPOINTS["fields"])
        df = pd.DataFrame(data)
        return df

    def get_field_production(
        self,
        field_name: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get field production data.

        Args:
            field_name: Filter by field name
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with production data
        """
        data = self._fetch(self.ENDPOINTS["field_production"])
        df = pd.DataFrame(data)

        # Filter
        if field_name:
            df = df[df["fieldName"].str.contains(field_name, case=False, na=False)]
        if start_year:
            df = df[df["year"] >= start_year]
        if end_year:
            df = df[df["year"] <= end_year]

        return df

    def get_wells(
        self,
        well_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get well data.

        Args:
            well_type: 'exploration', 'development', or 'other'
            status: Well status filter

        Returns:
            DataFrame with well data
        """
        data = self._fetch(self.ENDPOINTS["wells"])
        df = pd.DataFrame(data)

        if well_type:
            df = df[df["wellType"].str.lower() == well_type.lower()]
        if status:
            df = df[df["status"].str.contains(status, case=False, na=False)]

        return df

    def get_discoveries(self, status: Optional[str] = None) -> pd.DataFrame:
        """Get discoveries data."""
        data = self._fetch(self.ENDPOINTS["discoveries"])
        df = pd.DataFrame(data)

        if status:
            df = df[df["status"].str.contains(status, case=False, na=False)]

        return df


# Example usage
sodir = SODIRDataFetcher()

# Get all fields
fields = sodir.get_all_fields()
print(f"Total Norwegian fields: {len(fields)}")

# Get production for Johan Sverdrup
sverdrup_production = sodir.get_field_production(
    field_name="JOHAN SVERDRUP",
    start_year=2019
)
print(sverdrup_production)

# Get recent exploration wells
exploration_wells = sodir.get_wells(well_type="exploration")
print(f"Total exploration wells: {len(exploration_wells)}")
```
