---
name: metocean-data-fetcher
description: Fetch real-time and historical metocean data from NDBC, CO-OPS, Open-Meteo, ERDDAP, and MET Norway. Use for buoy data retrieval, tidal observations, marine forecasts, and multi-source data fusion.
---

# Metocean Data Fetcher Skill

Fetch real-time and historical ocean/weather data from multiple global sources for offshore energy operations, marine forecasting, and oceanographic analysis.

## When to Use

- Fetch buoy data, Get wave data, Download NDBC observations
- Get tidal data, Fetch currents from CO-OPS
- Get marine forecast, Download metocean time series
- Fetch historical waves, Get real-time oceanographic data
- Multi-source data fusion for validation
- Gulf of Mexico buoy surveys
- North Atlantic ocean forecasts

## Data Sources

| Source | Data Types | Client Class | API Type |
|--------|-----------|--------------|----------|
| NOAA NDBC | Waves, wind, SST, pressure, currents | `NDBCClient` | HTTP/Text |
| NOAA CO-OPS | Tides, water levels, currents, predictions | `COOPSClient` | REST JSON |
| Open-Meteo | Wave/swell/current forecasts (coordinate-based) | `OpenMeteoClient` | REST JSON |
| IOOS ERDDAP | Buoy, glider, HF radar, gridded data | `ERDDAPClient` | ERDDAP |
| MET Norway | Ocean/weather forecasts (North Atlantic/Arctic) | `MetNorwayClient` | REST JSON |

## YAML Configuration Templates

### Single Station Fetch (NDBC Buoy)

```yaml
metocean:
  source: ndbc
  station_id: "41001"  # Mid-Atlantic buoy
  fetch_type: realtime
  parameters:
    - wave_height
    - wave_period
    - wind_speed
    - wind_direction
    - sea_surface_temp
  output:
    format: csv
    path: "data/ndbc_41001.csv"
```

### Regional Station Discovery

```yaml
metocean:
  discovery:
    source: ndbc
    bbox:
      lon_min: -98
      lon_max: -88
      lat_min: 25
      lat_max: 31
    active_only: true
  output:
    format: json
    path: "data/gom_stations.json"
```

### Historical Time Series

```yaml
metocean:
  source: ndbc
  station_id: "41001"
  fetch_type: historical
  date_range:
    start: "2024-01-01"
    end: "2024-12-31"
  parameters:
    - wave_height
    - wave_period
    - wind_speed
  output:
    format: csv
    path: "data/historical_41001_2024.csv"
```

### Multi-Source Fusion

```yaml
metocean:
  fusion:
    sources:
      - source: ndbc
        station_id: "41001"
      - source: open_meteo
        coordinates:
          lat: 34.68
          lon: -72.66
    time_tolerance_minutes: 30
    merge_strategy: source_priority
  output:
    format: csv
    path: "data/fused_observations.csv"
```

### CO-OPS Tidal Data

```yaml
metocean:
  source: coops
  station_id: "8761724"  # Grand Isle, LA
  fetch_type: water_level
  date_range:
    start: "2024-01-01"
    end: "2024-01-31"
  datum: MLLW
  verified: true
  output:
    format: csv
    path: "data/grand_isle_tides.csv"
```

### Coordinate-Based Forecast (Open-Meteo)

```yaml
metocean:
  source: open_meteo
  coordinates:
    lat: 28.5
    lon: -88.5
  forecast_days: 7
  parameters:
    - wave_height
    - wave_period
    - wave_direction
    - swell_wave_height
    - ocean_current_velocity
  output:
    format: json
    path: "data/gom_forecast.json"
```

## Python API Examples

### NDBC Client

```python
from worldenergydata.metocean.clients.ndbc_client import NDBCClient

# Use context manager for proper cleanup
with NDBCClient() as client:
    # List stations in Gulf of Mexico
    gom_bbox = (-98.0, -88.0, 25.0, 31.0)
    result = client.fetch_stations(bbox=gom_bbox, active_only=True)
    for station in result.data[:10]:
        print(f"{station.station_id}: {station.name} ({station.latitude}, {station.longitude})")

    # Fetch real-time data from a buoy
    realtime = client.fetch_realtime(station_id="41001")
    for obs in realtime.data[:5]:
        print(f"{obs.observation_time}: {obs.wave_height_m}m waves, {obs.wind_speed_ms}m/s wind")

    # Fetch historical data (2024)
    from datetime import datetime
    historical = client.fetch_historical(
        station_id="41001",
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31)
    )
    print(f"Retrieved {historical.records_count} historical observations")

    # Get station metadata
    station = client.get_station_info("41001")
    print(f"Water depth: {station.water_depth_m}m, Owner: {station.owner}")

    # Fetch spectral wave data
    spectral = client.fetch_spectral("41001")
    print(f"Spectral records: {spectral.records_count}")
```

### CO-OPS Client

```python
from datetime import datetime, timedelta
from worldenergydata.metocean.clients.coops_client import COOPSClient

with COOPSClient() as client:
    # List tide stations in Gulf region
    gom_bbox = (-98.0, -80.0, 18.0, 31.0)
    stations = client.fetch_stations(bbox=gom_bbox)
    print(f"Found {stations.records_count} CO-OPS stations")

    # Fetch water level data
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 7)
    water_levels = client.fetch_water_level(
        station_id="8761724",  # Grand Isle, LA
        start_date=start,
        end_date=end,
        datum="MLLW",
        verified=True
    )
    for obs in water_levels.data[:5]:
        print(f"{obs.observation_time}: {obs.water_level_m:.3f}m ({obs.quality_flag})")

    # Fetch tide predictions
    predictions = client.fetch_tide_predictions(
        station_id="8761724",
        start_date=start,
        end_date=end,
        datum="MLLW",
        interval="hilo"  # High/low tides only
    )
    for pred in predictions.data:
        tide = "HIGH" if pred.tide_type == "H" else "LOW"
        print(f"{pred.prediction_time}: {tide} {pred.water_level_m:.2f}m")

    # Fetch current data (for current meter stations)
    currents = client.fetch_currents(
        station_id="s08010",
        start_date=start,
        end_date=end
    )

    # Get datum conversions for a station
    datums = client.fetch_datums("8761724")
    print(f"Available datums: {list(datums.keys())}")
```

### Open-Meteo Client

```python
from datetime import datetime, timedelta
from worldenergydata.metocean.clients.open_meteo_client import OpenMeteoClient

with OpenMeteoClient() as client:
    # Note: Open-Meteo uses coordinates, NOT stations
    # fetch_stations() returns empty result

    # Fetch 7-day marine forecast
    forecast = client.fetch_forecast(
        latitude=28.5,
        longitude=-88.5,
        forecast_days=7
    )
    for fc in forecast.data[:24]:  # First 24 hours
        print(f"{fc.forecast_time}: Wave={fc.wave_height_m}m, Swell={fc.swell_wave_height_m}m")

    # Fetch historical marine data (up to 92 days back)
    end = datetime.utcnow()
    start = end - timedelta(days=30)
    historical = client.fetch_historical(
        latitude=28.5,
        longitude=-88.5,
        start_date=start,
        end_date=end
    )
    print(f"Historical points: {historical.records_count}")

    # Fetch current conditions (1-day forecast)
    current = client.fetch_realtime_coords(
        latitude=28.5,
        longitude=-88.5
    )
    latest = current.data[0]
    print(f"Current: {latest.wave_height_m}m waves, {latest.current_speed_ms}m/s current")
```

### ERDDAP Client

```python
from datetime import datetime, timedelta
from worldenergydata.metocean.clients.erddap_client import ERDDAPClient

# Initialize with specific server
client = ERDDAPClient(server="gcoos")  # Gulf of Mexico

# Search for wave datasets
datasets = client.search_datasets("wave", bbox=(-98, -88, 25, 31))
for ds in datasets.data[:5]:
    print(f"{ds.dataset_id}: {ds.title}")

# Get dataset metadata
info = client.get_dataset_info("some_dataset_id")
print(f"Variables: {info.variables}")
print(f"Time coverage: {info.min_time} to {info.max_time}")

# Fetch tabular data
end = datetime.utcnow()
start = end - timedelta(days=7)
observations = client.fetch_tabledap(
    dataset_id="some_dataset_id",
    variables=["wave_height", "wave_period"],
    start_time=start,
    end_time=end,
    bbox=(-95, -90, 27, 30)
)

# Fetch gridded data
grid_data = client.fetch_griddap(
    dataset_id="gridded_dataset",
    variables=["sst", "ssh"],
    time_range=(start, end),
    lat_range=(25, 31),
    lon_range=(-98, -88)
)

# List all available datasets
all_datasets = client.list_datasets()
```

### MET Norway Client

```python
from worldenergydata.metocean.clients.met_norway_client import MetNorwayClient

with MetNorwayClient() as client:
    # Note: MET Norway uses coordinates, NOT stations
    # Good coverage for North Atlantic, Arctic, Nordic seas

    # Fetch ocean forecast (waves, currents, SST)
    ocean = client.fetch_ocean_forecast(
        latitude=60.0,
        longitude=5.0  # Bergen, Norway
    )
    for fc in ocean.data[:12]:
        print(f"{fc.forecast_time}: Wave={fc.wave_height_m}m, SST={fc.sea_surface_temp_c}C")

    # Fetch weather forecast (wind, pressure, temperature)
    weather = client.fetch_weather_forecast(
        latitude=60.0,
        longitude=5.0
    )
    for fc in weather.data[:12]:
        print(f"{fc.forecast_time}: Wind={fc.wind_speed_ms}m/s, Pressure={fc.pressure_hpa}hPa")

    # Fetch combined ocean + weather forecast
    combined = client.fetch_combined_forecast(
        latitude=60.0,
        longitude=5.0
    )
    for fc in combined.data[:6]:
        print(f"{fc.forecast_time}: Wave={fc.wave_height_m}m, Wind={fc.wind_speed_ms}m/s")
```

## External Tool Integration

### metocean-api (MET Norway NORA3/ERA5)

For hindcast and reanalysis data extraction from MET Norway archives.

```bash
pip install metocean-api
```

```python
from metocean_api.ts import TimeSeries

# Extract NORA3 wave hindcast
ts = TimeSeries(
    lon=5.0,
    lat=60.0,
    start_time='2020-01-01',
    end_time='2020-01-31',
    product='NORA3_wave'
)
ts.import_data(save_csv=True, save_nc=False)
df = ts.data

# Available products: NORA3_wave, NORA3_atm, ERA5, GTSM
```

### noaa-coops (Alternative CO-OPS Wrapper)

Simplified wrapper for NOAA CO-OPS data.

```bash
pip install noaa-coops
```

```python
import noaa_coops as nc

# Get water level data
station = nc.Station(id="8761724")
df = station.get_data(
    begin_date="20240101",
    end_date="20240131",
    product="water_level",
    datum="NAVD",
    units="metric",
    time_zone="gmt"
)

# Get tide predictions
predictions = station.get_data(
    begin_date="20240101",
    end_date="20240107",
    product="predictions",
    datum="MLLW"
)
```

### erddapy (Direct ERDDAP Access)

For advanced ERDDAP queries and custom data access.

```bash
pip install erddapy
```

```python
from erddapy import ERDDAP

e = ERDDAP(
    server="https://erddap.gcoos.org/erddap",
    protocol="tabledap"
)
e.dataset_id = "dataset_id_here"
e.variables = ["time", "latitude", "longitude", "wave_height"]
e.constraints = {
    "time>=": "2024-01-01",
    "time<=": "2024-01-31",
    "latitude>=": 25,
    "latitude<=": 31,
}
df = e.to_pandas()
```

## CLI Commands

### Station Management

```bash
# List available stations
wed metocean stations list --source ndbc --region gom --active
wed metocean stations list --source coops --region atlantic --limit 100

# Search by bounding box
wed metocean stations search --bbox -98,-88,25,31
wed metocean stations search --bbox -98,-88,25,31 --source ndbc

# Get station details
wed metocean stations info 41001 --source ndbc
wed metocean stations info 8761724 --source coops
```

### Data Fetching

```bash
# Fetch real-time NDBC data
wed metocean fetch ndbc 41001 --params wave,wind --hours 24
wed metocean fetch ndbc 41001 --output data/buoy_data.json

# Fetch CO-OPS tidal data
wed metocean fetch coops 8761724 --params water_level --hours 48 --datum MLLW

# Fetch Open-Meteo forecast (coordinate-based)
wed metocean fetch open-meteo 28.5,-88.5 --days 7 --params wave,swell,current
```

### Historical Data

```bash
# Fetch historical NDBC data
wed metocean historical 41001 2024-01-01 2024-12-31 --source ndbc --output historical.json

# Fetch historical CO-OPS data
wed metocean historical 8761724 2024-01-01 2024-01-31 --source coops --output tides.json

# Fetch historical Open-Meteo data (coordinate format)
wed metocean historical 28.5,-88.5 2024-01-01 2024-03-31 --source open-meteo
```

### Export Commands

```bash
# Export to CSV
wed metocean export csv -o output.csv -s 41001 --source ndbc --start 2024-01-01 --end 2024-12-31

# Export to JSON
wed metocean export json -o output.json -s 41001 --source ndbc

# Export to NetCDF (requires netCDF4 package)
wed metocean export netcdf -o output.nc -s 41001 --source ndbc
```

### Cache Management

```bash
# View cache status
wed metocean cache status

# Clear all cache
wed metocean cache clear --yes

# Clear specific source cache
wed metocean cache clear --source ndbc --yes

# Remove expired entries
wed metocean cache cleanup
```

### Database Management

```bash
# Initialize database schema
wed metocean db init

# Force recreate tables
wed metocean db init --force

# Show database status
wed metocean db status
```

### Information Commands

```bash
# Module information
wed metocean info

# Show configuration status
wed metocean status
```

## Output Formats

### CSV Exporter

```python
from pathlib import Path
from worldenergydata.metocean.exporters.csv_exporter import CSVExporter
from worldenergydata.metocean.processors.data_harmonizer import DataHarmonizer

# Harmonize observations first
harmonizer = DataHarmonizer(apply_quality_checks=True)
harmonized = harmonizer.harmonize_batch(ndbc_observations, DataSource.NDBC)

# Export to CSV
exporter = CSVExporter(include_quality=True)
count = exporter.export(harmonized, Path("output.csv"))

# Export with date filtering
from datetime import datetime
count = exporter.export(
    harmonized,
    Path("filtered.csv"),
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 6, 30)
)

# Export summary statistics
count = exporter.export_summary(
    harmonized,
    Path("summary.csv"),
    group_by="day"  # "hour", "day", or "station"
)
```

### JSON Exporter

```python
from worldenergydata.metocean.exporters.json_exporter import JSONExporter

exporter = JSONExporter()

# Standard JSON export
exporter.export(harmonized, Path("data.json"))

# GeoJSON export (for mapping)
exporter.export_geojson(harmonized, Path("data.geojson"))
```

### NetCDF Exporter

```python
from worldenergydata.metocean.exporters.netcdf_exporter import NetCDFExporter

# Requires: pip install netCDF4
exporter = NetCDFExporter()
exporter.export(harmonized, Path("data.nc"))  # CF-compliant NetCDF
```

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
    observations,
    time_tolerance_minutes=30
)
print(f"Merged {len(observations)} into {len(merged)} records")

# Access harmonized fields
for obs in merged:
    print(f"Source: {obs.source.value}")
    print(f"Time: {obs.observation_time}")
    print(f"Wave: {obs.wave_height_m}m @ {obs.wave_period_s}s")
    print(f"Wind: {obs.wind_speed_ms}m/s from {obs.wind_direction_deg}")
    print(f"Quality: {obs.quality_flag.value}")
    if obs.quality_issues:
        print(f"Issues: {obs.quality_issues}")
```

## Best Practices

1. **Use caching** - Built-in cache with 24-hour TTL reduces API load
2. **Respect rate limits** - Clients implement automatic rate limiting
3. **Use `fetch_realtime` for recent data** - Last 45 days for NDBC
4. **Use `fetch_historical` for archived data** - NDBC archives go back years
5. **Coordinate-based sources have no stations** - Open-Meteo and MET Norway
6. **Check quality flags** - Harmonized observations include quality assessment
7. **Batch operations** - Use `harmonize_batch` for efficiency
8. **Context managers** - Always use `with` statement for clients

## Common Workflows

### 1. Gulf of Mexico Buoy Survey

```python
from worldenergydata.metocean.clients.ndbc_client import NDBCClient
from worldenergydata.metocean.exporters.csv_exporter import CSVExporter

# Discover and fetch all GOM buoys
with NDBCClient() as client:
    gom = (-98, -80, 18, 31)
    stations = client.fetch_stations(bbox=gom, active_only=True)

    all_obs = []
    for station in stations.data[:10]:  # Limit for demo
        result = client.fetch_realtime(station.station_id)
        all_obs.extend(result.data)

# Export combined data
exporter = CSVExporter()
exporter.export(all_obs, "gom_survey.csv")
```

### 2. Tidal Analysis (Observation vs Prediction)

```python
from datetime import datetime
from worldenergydata.metocean.clients.coops_client import COOPSClient

with COOPSClient() as client:
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 7)

    # Get observed water levels
    observed = client.fetch_water_level("8761724", start, end, datum="MLLW")

    # Get tide predictions
    predicted = client.fetch_tide_predictions("8761724", start, end, datum="MLLW")

    # Compare (simplified)
    print(f"Observations: {observed.records_count}")
    print(f"Predictions: {predicted.records_count}")
```

### 3. Forecast Validation (Forecast vs Observation)

```python
from worldenergydata.metocean.clients.ndbc_client import NDBCClient
from worldenergydata.metocean.clients.open_meteo_client import OpenMeteoClient
from worldenergydata.metocean.processors.data_harmonizer import DataHarmonizer

# Get buoy observations
with NDBCClient() as ndbc:
    station = ndbc.get_station_info("41001")
    obs_result = ndbc.fetch_realtime("41001")

# Get forecast for same location
with OpenMeteoClient() as ometeo:
    fc_result = ometeo.fetch_realtime_coords(
        latitude=station.latitude,
        longitude=station.longitude
    )

# Harmonize and merge for comparison
harmonizer = DataHarmonizer()
obs_harmonized = harmonizer.harmonize_batch(obs_result.data, DataSource.NDBC)
fc_harmonized = harmonizer.harmonize_batch(fc_result.data, DataSource.OPEN_METEO)

# Merge by time
all_data = obs_harmonized + fc_harmonized
merged = harmonizer.merge_observations(all_data, time_tolerance_minutes=60)
```

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - BSEE offshore data
- [marine-safety-incidents](../marine-safety-incidents/SKILL.md) - Marine safety analysis
- [field-analyzer](../field-analyzer/SKILL.md) - Offshore field analysis
- [energy-data-visualizer](../energy-data-visualizer/SKILL.md) - Data visualization

## References

- NDBC: https://www.ndbc.noaa.gov/
- CO-OPS: https://tidesandcurrents.noaa.gov/
- Open-Meteo: https://open-meteo.com/en/docs/marine-weather-api
- ERDDAP: https://coastwatch.pfeg.noaa.gov/erddap/
- MET Norway: https://api.met.no/
