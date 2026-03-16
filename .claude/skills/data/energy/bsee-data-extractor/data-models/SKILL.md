---
name: bsee-data-extractor-data-models
description: 'Sub-skill of bsee-data-extractor: Data Models (+5).'
version: 1.0.0
category: data/energy
type: reference
scripts_exempt: true
---

# Data Models (+5)

## Data Models


```python
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, Any
from enum import Enum
import pandas as pd

class ProductType(Enum):
    """Production fluid types."""
    OIL = "oil"

*See sub-skills for full details.*

## WAR/APD Data Models (continued)


```python
    def to_dataframe(self) -> pd.DataFrame:
        """Convert production records to DataFrame."""
        data = []
        for rec in self.records:
            data.append({
                'date': rec.production_date,
                'oil_bbls': rec.oil_bbls,
                'gas_mcf': rec.gas_mcf,
                'water_bbls': rec.water_bbls,

*See sub-skills for full details.*

## BSEE Data Client


```python
import requests
import zipfile
import io
from pathlib import Path
from typing import Optional, List, Dict, Generator
import pandas as pd
import logging

logger = logging.getLogger(__name__)

*See sub-skills for full details.*

## Production Aggregator


```python
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from datetime import date

class ProductionAggregator:
    """
    Aggregate production data across wells, fields, or time periods.
    """

*See sub-skills for full details.*

## Activity Aggregator


```python
from typing import Dict, List
import pandas as pd

class ActivityAggregator:
    """
    Aggregate WAR and APD data across wells, fields, or time periods.
    """

    def __init__(self, activities: List[WellActivity]):

*See sub-skills for full details.*

## Report Generator


```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

class BSEEReportGenerator:
    """Generate interactive HTML reports for BSEE data."""

    def __init__(self, aggregator: ProductionAggregator):
        """

*See sub-skills for full details.*
