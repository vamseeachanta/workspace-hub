---
name: sodir-data-extractor
description: SODIR Data Extractor (user)
---

# SODIR Data Extractor Skill

> Extract and process Norwegian Petroleum Directorate (SODIR) field and production data

## When to Use This Skill

Use this skill when you need to:
- Extract Norwegian continental shelf field data
- Query SODIR production statistics
- Compare Norwegian fields with GOM fields
- Build cross-basin analysis datasets
- Access historical NCS field performance

## Core Pattern

```python
"""
ABOUTME: Norwegian Petroleum Directorate (SODIR) data extraction
ABOUTME: Provides field and production data from the Norwegian Continental Shelf
"""

from dataclasses import dataclass
from typing import List, Optional
import requests
import pandas as pd


@dataclass
class SODIRField:
    """Norwegian field information."""
    field_name: str
    discovery_year: int
    status: str  # PRODUCING, SHUT DOWN, etc.
    operator: str
    area_name: str  # Quadrant/block area
    water_depth_m: float
    recoverable_oil_mmbbl: float
    recoverable_gas_bcm: float


@dataclass
class SODIRProduction:
    """Monthly production record."""
    field_name: str
    year: int
    month: int
    oil_kbbl: float
    gas_msm3: float
    ngl_kbbl: float
    condensate_kbbl: float
    water_kbbl: float


class SODIRDataClient:
    """
    Client for SODIR (Norwegian Petroleum Directorate) data.

    Data sources:
    - https://factpages.sodir.no/
    - Public API and downloadable datasets
    """

    BASE_URL = "https://factpages.sodir.no/api"

    def __init__(self, cache_dir: str = ".cache/sodir"):
        self.cache_dir = cache_dir

    def get_field_list(self, status: str = None) -> List[SODIRField]:
        """
        Get list of Norwegian fields.

        Args:
            status: Filter by status (PRODUCING, SHUT DOWN, etc.)

        Returns:
            List of SODIRField objects
        """
        # Download field data from SODIR
        url = f"{self.BASE_URL}/field"
        response = requests.get(url)
        data = response.json()

        fields = []
        for item in data:
            if status and item.get("status") != status:
                continue

            fields.append(SODIRField(
                field_name=item["fldName"],
                discovery_year=item.get("fldDiscoveryYear", 0),
                status=item.get("fldStatus", ""),
                operator=item.get("cmpLongName", ""),
                area_name=item.get("fldArea", ""),
                water_depth_m=item.get("fldWaterDepth", 0),
                recoverable_oil_mmbbl=item.get("fldRecoverableOil", 0),
                recoverable_gas_bcm=item.get("fldRecoverableGas", 0)
            ))

        return fields

    def get_field_production(
        self,
        field_name: str,
        start_year: int = None,
        end_year: int = None
    ) -> pd.DataFrame:
        """
        Get monthly production for a field.

        Args:
            field_name: SODIR field name
            start_year: Optional start year filter
            end_year: Optional end year filter

        Returns:
            DataFrame with monthly production
        """
        url = f"{self.BASE_URL}/field/{field_name}/production"
        response = requests.get(url)
        data = response.json()

        records = []
        for item in data:
            year = item.get("prfYear", 0)
            if start_year and year < start_year:
                continue
            if end_year and year > end_year:
                continue

            records.append(SODIRProduction(
                field_name=field_name,
                year=year,
                month=item.get("prfMonth", 1),
                oil_kbbl=item.get("prfPrdOilNetMillSm3", 0) * 6.29,
                gas_msm3=item.get("prfPrdGasNetBillSm3", 0),
                ngl_kbbl=item.get("prfPrdNGLNetMillSm3", 0) * 6.29,
                condensate_kbbl=item.get("prfPrdCondensateNetMillSm3", 0) * 6.29,
                water_kbbl=item.get("prfPrdProducedWaterInFieldMillSm3", 0) * 6.29
            ))

        df = pd.DataFrame([vars(r) for r in records])
        df["date"] = pd.to_datetime(
            df[["year", "month"]].assign(day=1)
        )
        return df.sort_values("date")

    def compare_with_gom(
        self,
        ncs_field: str,
        gom_api: str
    ) -> pd.DataFrame:
        """
        Compare NCS field with GOM well production.

        Returns aligned production comparison.
        """
        # Get NCS data
        ncs_df = self.get_field_production(ncs_field)

        # Get GOM data (via BSEE client)
        from worldenergydata.bsee.data import get_production_data
        gom_df = get_production_data(api_number=gom_api)

        # Align by months on production
        ncs_df["months"] = range(len(ncs_df))
        gom_df["months"] = range(len(gom_df))

        comparison = pd.merge(
            ncs_df[["months", "oil_kbbl"]].rename(columns={"oil_kbbl": "ncs_oil"}),
            gom_df[["months", "oil_bbl"]].rename(columns={"oil_bbl": "gom_oil"}),
            on="months",
            how="outer"
        )

        return comparison
```

## YAML Configuration Template

```yaml
# config/input/sodir-extraction.yaml

metadata:
  feature_name: "sodir-extraction"
  created: "2025-01-15"

data_source:
  type: "sodir"
  cache_enabled: true
  cache_ttl_days: 7

query:
  fields:
    - "JOHAN SVERDRUP"
    - "TROLL"
    - "EKOFISK"
  status_filter: "PRODUCING"
  start_year: 2015
  end_year: null

output:
  format: "csv"
  path: "data/sodir/"
  include_metadata: true
```

## CLI Usage

```bash
# Extract field list
python -m worldenergydata.sodir \
    --action list-fields \
    --status PRODUCING \
    --output data/sodir/fields.csv

# Get production data
python -m worldenergydata.sodir \
    --action production \
    --field "JOHAN SVERDRUP" \
    --start-year 2019 \
    --output data/sodir/johan_sverdrup.csv
```

## Best Practices

1. Cache SODIR data locally to reduce API calls
2. Use field names exactly as they appear in SODIR
3. Convert units (Sm3 to bbl) for comparison with BSEE data
4. Handle missing data gracefully for early production periods
