---
name: metocean-data-fetcher-station-management
description: 'Sub-skill of metocean-data-fetcher: Station Management (+6).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Station Management (+6)

## Station Management


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

## Data Fetching


```bash
# Fetch real-time NDBC data
wed metocean fetch ndbc 41001 --params wave,wind --hours 24
wed metocean fetch ndbc 41001 --output data/buoy_data.json

# Fetch CO-OPS tidal data
wed metocean fetch coops 8761724 --params water_level --hours 48 --datum MLLW

# Fetch Open-Meteo forecast (coordinate-based)
wed metocean fetch open-meteo 28.5,-88.5 --days 7 --params wave,swell,current
```

## Historical Data


```bash
# Fetch historical NDBC data
wed metocean historical 41001 2024-01-01 2024-12-31 --source ndbc --output historical.json

# Fetch historical CO-OPS data
wed metocean historical 8761724 2024-01-01 2024-01-31 --source coops --output tides.json

# Fetch historical Open-Meteo data (coordinate format)
wed metocean historical 28.5,-88.5 2024-01-01 2024-03-31 --source open-meteo
```

## Export Commands


```bash
# Export to CSV
wed metocean export csv -o output.csv -s 41001 --source ndbc --start 2024-01-01 --end 2024-12-31

# Export to JSON
wed metocean export json -o output.json -s 41001 --source ndbc

# Export to NetCDF (requires netCDF4 package)
wed metocean export netcdf -o output.nc -s 41001 --source ndbc
```

## Cache Management


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

## Database Management


```bash
# Initialize database schema
wed metocean db init

# Force recreate tables
wed metocean db init --force

# Show database status
wed metocean db status
```

## Information Commands


```bash
# Module information
wed metocean info

# Show configuration status
wed metocean status
```
