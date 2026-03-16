---
name: metocean-data-fetcher-metocean-api-met-norway-nora3era5
description: 'Sub-skill of metocean-data-fetcher: metocean-api (MET Norway NORA3/ERA5)
  (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# metocean-api (MET Norway NORA3/ERA5) (+2)

## metocean-api (MET Norway NORA3/ERA5)


For hindcast and reanalysis data extraction from MET Norway archives.

```bash
pip install metocean-api
```

```python
from metocean_api.ts import TimeSeries

# Extract NORA3 wave hindcast

*See sub-skills for full details.*

## noaa-coops (Alternative CO-OPS Wrapper)


Simplified wrapper for NOAA CO-OPS data.

```bash
pip install noaa-coops
```

```python
import noaa_coops as nc

# Get water level data

*See sub-skills for full details.*

## erddapy (Direct ERDDAP Access)


For advanced ERDDAP queries and custom data access.

```bash
pip install erddapy
```

```python
from erddapy import ERDDAP

e = ERDDAP(

*See sub-skills for full details.*
