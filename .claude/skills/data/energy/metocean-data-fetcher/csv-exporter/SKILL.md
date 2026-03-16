---
name: metocean-data-fetcher-csv-exporter
description: 'Sub-skill of metocean-data-fetcher: CSV Exporter (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# CSV Exporter (+2)

## CSV Exporter


```python
from pathlib import Path
from worldenergydata.metocean.exporters.csv_exporter import CSVExporter
from worldenergydata.metocean.processors.data_harmonizer import DataHarmonizer

# Harmonize observations first
harmonizer = DataHarmonizer(apply_quality_checks=True)
harmonized = harmonizer.harmonize_batch(ndbc_observations, DataSource.NDBC)

# Export to CSV

*See sub-skills for full details.*

## JSON Exporter


```python
from worldenergydata.metocean.exporters.json_exporter import JSONExporter

exporter = JSONExporter()

# Standard JSON export
exporter.export(harmonized, Path("data.json"))

# GeoJSON export (for mapping)
exporter.export_geojson(harmonized, Path("data.geojson"))
```

## NetCDF Exporter


```python
from worldenergydata.metocean.exporters.netcdf_exporter import NetCDFExporter

# Requires: pip install netCDF4
exporter = NetCDFExporter()
exporter.export(harmonized, Path("data.nc"))  # CF-compliant NetCDF
```
