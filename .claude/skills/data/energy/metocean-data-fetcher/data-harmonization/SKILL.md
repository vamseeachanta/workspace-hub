---
name: metocean-data-fetcher-data-harmonization
description: 'Sub-skill of metocean-data-fetcher: Data Harmonization.'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Data Harmonization

## Data Harmonization


Standardize data from multiple sources to a common format.

```python
from worldenergydata.metocean.processors.data_harmonizer import DataHarmonizer
from worldenergydata.metocean.constants import DataSource

harmonizer = DataHarmonizer(apply_quality_checks=True)

# Convert NDBC observation to standard format
standardized = harmonizer.harmonize_ndbc(
    ndbc_obs,
    latitude=34.68,
    longitude=-72.66
)

# Batch conversion
harmonized_list = harmonizer.harmonize_batch(
    observations,
    source=DataSource.NDBC,
    station_coords={"41001": (34.68, -72.66)}
)

# Merge observations from multiple sources
# Groups by time/location within tolerance
merged = harmonizer.merge_observations(

*See sub-skills for full details.*
