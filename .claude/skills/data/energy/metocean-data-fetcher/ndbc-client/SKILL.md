---
name: metocean-data-fetcher-ndbc-client
description: 'Sub-skill of metocean-data-fetcher: NDBC Client (+4).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# NDBC Client (+4)

## NDBC Client


```python
from worldenergydata.metocean.clients.ndbc_client import NDBCClient

# Use context manager for proper cleanup
with NDBCClient() as client:
    # List stations in Gulf of Mexico
    gom_bbox = (-98.0, -88.0, 25.0, 31.0)
    result = client.fetch_stations(bbox=gom_bbox, active_only=True)
    for station in result.data[:10]:
        print(f"{station.station_id}: {station.name} ({station.latitude}, {station.longitude})")

*See sub-skills for full details.*

## CO-OPS Client


```python
from datetime import datetime, timedelta
from worldenergydata.metocean.clients.coops_client import COOPSClient

with COOPSClient() as client:
    # List tide stations in Gulf region
    gom_bbox = (-98.0, -80.0, 18.0, 31.0)
    stations = client.fetch_stations(bbox=gom_bbox)
    print(f"Found {stations.records_count} CO-OPS stations")


*See sub-skills for full details.*

## Open-Meteo Client


```python
from datetime import datetime, timedelta
from worldenergydata.metocean.clients.open_meteo_client import OpenMeteoClient

with OpenMeteoClient() as client:
    # Note: Open-Meteo uses coordinates, NOT stations
    # fetch_stations() returns empty result

    # Fetch 7-day marine forecast
    forecast = client.fetch_forecast(

*See sub-skills for full details.*

## ERDDAP Client


```python
from datetime import datetime, timedelta
from worldenergydata.metocean.clients.erddap_client import ERDDAPClient

# Initialize with specific server
client = ERDDAPClient(server="gcoos")  # Gulf of Mexico

# Search for wave datasets
datasets = client.search_datasets("wave", bbox=(-98, -88, 25, 31))
for ds in datasets.data[:5]:

*See sub-skills for full details.*

## MET Norway Client


```python
from worldenergydata.metocean.clients.met_norway_client import MetNorwayClient

with MetNorwayClient() as client:
    # Note: MET Norway uses coordinates, NOT stations
    # Good coverage for North Atlantic, Arctic, Nordic seas

    # Fetch ocean forecast (waves, currents, SST)
    ocean = client.fetch_ocean_forecast(
        latitude=60.0,

*See sub-skills for full details.*
