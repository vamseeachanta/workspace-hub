---
name: metocean-data-fetcher-1-gulf-of-mexico-buoy-survey
description: 'Sub-skill of metocean-data-fetcher: 1. Gulf of Mexico Buoy Survey (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Gulf of Mexico Buoy Survey (+2)

## 1. Gulf of Mexico Buoy Survey


```python
from worldenergydata.metocean.clients.ndbc_client import NDBCClient
from worldenergydata.metocean.exporters.csv_exporter import CSVExporter

# Discover and fetch all GOM buoys
with NDBCClient() as client:
    gom = (-98, -80, 18, 31)
    stations = client.fetch_stations(bbox=gom, active_only=True)

    all_obs = []

*See sub-skills for full details.*

## 2. Tidal Analysis (Observation vs Prediction)


```python
from datetime import datetime
from worldenergydata.metocean.clients.coops_client import COOPSClient

with COOPSClient() as client:
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 7)

    # Get observed water levels
    observed = client.fetch_water_level("8761724", start, end, datum="MLLW")

*See sub-skills for full details.*

## 3. Forecast Validation (Forecast vs Observation)


```python
from worldenergydata.metocean.clients.ndbc_client import NDBCClient
from worldenergydata.metocean.clients.open_meteo_client import OpenMeteoClient
from worldenergydata.metocean.processors.data_harmonizer import DataHarmonizer

# Get buoy observations
with NDBCClient() as ndbc:
    station = ndbc.get_station_info("41001")
    obs_result = ndbc.fetch_realtime("41001")


*See sub-skills for full details.*
