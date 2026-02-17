# Plan: Refresh All BSEE Data

## Executive Summary

Refresh all BSEE (Bureau of Safety and Environmental Enforcement) data to enable up-to-date analysis of any GOM field or lease. Current data is **5 months stale** (last updated August 18, 2025).

## Current State

| Data Type | Last Updated | Size | Source URL |
|-----------|--------------|------|------------|
| Well APD | 2025-08-18 | ~5-10 MB | data.bsee.gov/Well/Files/APDRawData.zip |
| Production | 2025-08-18 | ~15-50 MB | data.bsee.gov/Production/Files/ProductionRawData.zip |
| WAR | Unknown | ~120+ MB | data.bsee.gov/Well/Files/eWellWARRawData.zip |

**Binary data directories:** 31 subdirectories in `data/modules/bsee/bin/`

## Implementation Plan - Incremental Testing

**Strategy:** Test existing scripts incrementally, smallest files first, learn from failures.

---

### Step 1: Test URL Connectivity (No Downloads)

**Goal:** Verify BSEE URLs are accessible and get file metadata.

```python
# Test script - run in Python REPL or as script
from worldenergydata.bsee.data.scrapers.bsee_web import BSEEWebScraper

scraper = BSEEWebScraper()

# Step 1a: Verify all URLs accessible (HEAD requests only)
results = scraper.verify_all_sources()
for name, info in results.items():
    print(f"{name}: {'✓' if info['accessible'] else '✗'} {info['url']}")

# Step 1b: Get file sizes without downloading
for data_type in ['well', 'production', 'war']:
    info = scraper.get_file_info(scraper.URLS[data_type])
    print(f"{data_type}: {info.get('size_mb', 'N/A'):.1f} MB, Last-Modified: {info.get('last_modified', 'N/A')}")
```

**Expected Output:**
- well: ✓ accessible, ~5-10 MB
- production: ✓ accessible, ~15-50 MB
- war: ✓ accessible, ~100+ MB
- portal: ✓ accessible

**Possible Errors:**
- Network timeout → Check firewall/VPN
- SSL certificate error → May need `verify=False` temporarily
- 403 Forbidden → User-Agent header issue

---

### Step 2: Test APD Download (Smallest File)

**Goal:** Download smallest file (~5-10 MB) to verify download mechanism works.

```python
from worldenergydata.bsee.data.scrapers.bsee_web import BSEEWebScraper

scraper = BSEEWebScraper()

# Download well APD data (smallest, ~5-10 MB)
data = scraper.download_well_data()

if data:
    print(f"✓ Downloaded {len(data) / (1024*1024):.2f} MB")

    # Verify it's a valid zip
    import zipfile
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        print(f"✓ Valid ZIP with {len(zf.namelist())} files:")
        for name in zf.namelist()[:5]:
            print(f"  - {name}")
else:
    print("✗ Download failed")
```

**Expected:** ~5-10 MB downloaded, valid ZIP with CSV files inside.

**Timeout:** 10 minutes max (600s)

---

### Step 3: Test Production Download (Medium File)

**Goal:** Download production data (~15-50 MB).

```python
from worldenergydata.bsee.data.scrapers.bsee_web import BSEEWebScraper

scraper = BSEEWebScraper()

# Download production data (medium, ~15-50 MB)
data = scraper.download_production_data()

if data:
    print(f"✓ Downloaded {len(data) / (1024*1024):.2f} MB")

    import zipfile
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        print(f"✓ Valid ZIP with {len(zf.namelist())} files")
else:
    print("✗ Download failed")
```

**Timeout:** 20 minutes max (1200s)

---

### Step 4: Test WAR Download (Largest File)

**Goal:** Download WAR data (~120+ MB) - only after smaller files succeed.

```python
from worldenergydata.bsee.data.scrapers.bsee_web import BSEEWebScraper

scraper = BSEEWebScraper()

# Download WAR data (largest, ~120+ MB)
# This may take 10-40 minutes
data = scraper.download_war_data()

if data:
    print(f"✓ Downloaded {len(data) / (1024*1024):.2f} MB")
else:
    print("✗ Download failed")
```

**Timeout:** 40 minutes max (2400s) with adaptive increase on retry.

---

### Step 5: Run Full Data Refresh (After Downloads Work)

Once all downloads succeed, run the enhanced data refresh:

```yaml
# Create config file: config/input/bsee_refresh.yaml
meta:
  mode: enhanced

data:
  well: true
  production: true
  war: true  # Optional - skip if timeouts
```

```bash
# Run the refresh
cd /mnt/github/workspace-hub/worldenergydata
uv run python -c "
from worldenergydata.bsee.data.refresh.data_refresh_enhanced import DataRefreshEnhanced
import yaml

with open('config/input/bsee_refresh.yaml') as f:
    cfg = yaml.safe_load(f)

refresher = DataRefreshEnhanced()
refresher.router(cfg)
"
```

---

### Step 6: Verify Data Updated

```bash
# Check binary file timestamps
stat data/modules/bsee/bin/apd/*.bin
stat data/modules/bsee/bin/production_raw/*.bin

# Should show today's date (2026-01-18)
```

---

## Critical Files

| File | Purpose |
|------|---------|
| `src/worldenergydata/modules/bsee/data/scrapers/bsee_web.py` | Web scraper with download methods |
| `src/worldenergydata/modules/bsee/data/refresh/data_refresh_enhanced.py` | Enhanced refresh with parallel processing |
| `src/worldenergydata/modules/bsee/data/cache/chunk_manager.py` | Change detection and caching |
| `data/modules/bsee/bin/` | Binary data output directory |

## Available Methods in BSEEWebScraper

| Method | Purpose | Timeout |
|--------|---------|---------|
| `verify_all_sources()` | Check URL accessibility (HEAD only) | 30s |
| `get_file_info(url)` | Get file size/metadata (HEAD only) | 30s |
| `download_well_data()` | Download APD data | 10 min |
| `download_production_data()` | Download production data | 20 min |
| `download_war_data()` | Download WAR data | 40 min |

## Success Criteria

- [ ] Step 1: All BSEE URLs accessible
- [ ] Step 2: APD data downloads successfully (~5-10 MB)
- [ ] Step 3: Production data downloads successfully (~15-50 MB)
- [ ] Step 4: WAR data downloads successfully (~120+ MB)
- [ ] Step 5: Binary files updated with current timestamps
- [ ] Step 6: Integration tests pass

## Error Handling

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| `Timeout` | File too large, slow connection | Increase timeout, retry |
| `403 Forbidden` | User-Agent blocked | Check headers |
| `SSL Error` | Certificate issue | May need `verify=False` |
| `ConnectionError` | Network/firewall | Check VPN, firewall |

## Skills Available

- **`bsee-data-extractor`** - After refresh, use to query data by API, block, lease, or field
