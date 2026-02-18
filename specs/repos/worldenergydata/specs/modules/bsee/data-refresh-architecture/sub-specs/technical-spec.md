# Technical Specification

This is the technical specification for the spec detailed in @specs/modules/bsee/data-refresh-architecture/spec.md

> Created: 2025-08-06
> Version: 1.0.0

## Technical Requirements

### Primary Research Requirement
- **API Discovery:** Conduct comprehensive research of BSEE data access methods to identify any available web APIs
- **API Testing:** If APIs exist, create comprehensive test suite demonstrating API access capabilities
- **Fallback Implementation:** If no APIs exist, implement web scraping solution

### Core Functionality (Based on Existing Architecture)
- **Direct Data Links Access:** Access the three confirmed BSEE data sources:
  - WELL_DATA: https://www.data.bsee.gov/Well/Files/APDRawData.zip (daily updates)
  - PRODUCTION_DATA: https://www.data.bsee.gov/Production/Files/ProductionRawData.zip (bi-monthly updates) 
  - WAR_DATA: https://www.data.bsee.gov/Well/Files/eWellWARRawData.zip (daily updates)
- **In-Memory Processing:** Process 100+ MB files without storing zip files in repository due to GitHub limits
- **Existing Pipeline Integration:** Maintain compatibility with current execution path and binary output format
- **Config File Compatibility:** Support existing YAML configurations and flag-based processing

### Performance Requirements
- Process 100+ MB BSEE files in-memory without storing intermediate files
- Maintain memory efficiency during large file processing (streaming where possible)
- Preserve existing binary file generation speed using pickle serialization
- Support the three data types (well, production, war) with existing flag-based control

### Integration Requirements
- **Existing Test Entry Point:** Maintain compatibility with `tests/modules/bsee/data/refresh/data_refresh_test.py`
- **Config File Integration:** Work with existing configurations:
  - `tests/modules/bsee/data/refresh/data_refresh.yml` (data refresh and apm flags)
  - `src/worldenergydata/base_configs/modules/bsee/bsee.yml` (file paths)
- **Execution Path Compatibility:** Integrate with existing flow:
  - `engine.py` → `bsee.py` → `bsee_data.py` → `data_refresh.py`
- **Binary Output Compatibility:** Maintain existing pickle-based binary file format in `data/modules/bsee/bin`

### Data Source Specifications
- **BSEE Main Portal:** https://www.data.bsee.gov/Main/RawData.aspx
- **Data Location:** Links found in "Raw Data" column under "Delimited" button
- **Display Names in Portal:**
  - "Application for Permit to Drill" → WELL_DATA
  - "Production Data" → PRODUCTION_DATA  
  - "eWell Submissions WAR" → WAR_DATA
- **Update Frequencies:** Daily (well & war), Bi-monthly (production)
- **File Constraints:** Cannot store 100+ MB zip files in GitHub repository

## Approach Options

**Option A: API Integration (Preferred if available)**
- Pros: Direct data access, no file handling, always current data, efficient
- Cons: Depends on BSEE offering APIs (requires research to confirm)

**Option B: In-Memory Web Scraping (Selected if no APIs)**
- Pros: Bypasses zip file storage, accesses latest data, maintains existing binary format
- Cons: Higher memory usage, depends on website structure stability

**Option C: Current Zip File Approach (Existing)**
- Pros: Currently implemented, stable
- Cons: Stale data causes "big variance" in analysis, large file storage issues

**Rationale:** API integration is preferred to eliminate file handling entirely. If APIs don't exist, in-memory processing solves the core problems: data freshness and repository size constraints, while maintaining compatibility with existing pickle-based processing.

## External Dependencies

### New Dependencies

- **httpx (^0.25.0)** - Modern async HTTP client for web scraping
  - **Justification:** Better than requests for async operations, built-in retry support
  
- **selectolax (^0.3.0)** - Fast HTML parser
  - **Justification:** 10x faster than BeautifulSoup for large HTML parsing
  
- **tenacity (^8.2.0)** - Retry library with advanced features
  - **Justification:** Sophisticated retry logic with exponential backoff

- **rich (^13.0.0)** - Terminal formatting and progress bars
  - **Justification:** Professional CLI output with minimal code

### Existing Dependencies (Verified)
- pandas - Data manipulation
- numpy - Numerical operations
- loguru - Logging
- pyyaml - Configuration parsing
- selenium - Complex web interactions (when needed)
- scrapy - Advanced web scraping framework

## Architecture Design

### Module Structure (Integration with Existing)
```
# Existing structure maintained:
src/worldenergydata/modules/bsee/data/
├── refresh/
│   ├── data_refresh.py          # Enhanced with API/scraping logic
│   ├── api_client.py            # New: API research and implementation
│   └── web_scraper.py           # New: In-memory scraping if no APIs
├── _from_zip/
│   ├── well_data.py             # Existing: Enhanced to use fresh data
│   └── production_data.py       # Existing: Enhanced to use fresh data
└── bsee_data.py                 # Existing: Entry point for data processing

# Supporting files:
tests/modules/bsee/data/refresh/
├── data_refresh_test.py         # Existing: Test entry point
└── data_refresh.yml             # Existing: Configuration with refresh/apm flags

src/worldenergydata/base_configs/modules/bsee/
└── bsee.yml                     # Existing: File paths configuration
```

### Class Hierarchy
```
DataSource (ABC)
├── WebScraperSource
│   ├── BSEEQueryScraper
│   └── BSEETableScraper
├── FileDownloadSource
│   ├── ZipFileDownloader
│   └── CSVFileDownloader
└── APISource (future)
    └── BSEEAPIClient
```

### Data Flow (Enhanced Existing Architecture)
1. **Test Execution** → `data_refresh_test.py` initiates refresh process
2. **Engine Flow** → `engine.py` → `bsee.py` → `bsee_data.py` → `data_refresh.py`
3. **Flag Processing** → Check data refresh flag, apm flag, production flag from YAML configs
4. **Data Source Selection** → Choose API (if available) or web scraping for fresh data
5. **In-Memory Processing** → Process 100+ MB files without local zip storage
6. **Binary Generation** → Use existing `_from_zip/well_data.py` and `production_data.py` with fresh data
7. **Pickle Serialization** → Output binary files to `data/modules/bsee/bin` as current system

## Configuration Schema

```yaml
# Enhanced configuration maintaining existing structure:

# From tests/modules/bsee/data/refresh/data_refresh.yml
data: 
  refresh: true     # Existing flag
  apm: true        # Existing flag for well data processing
  production: true # Existing flag for production data processing

# Enhanced with new data source configuration
bsee_data_sources:
  well_data:
    url: "https://www.data.bsee.gov/Well/Files/APDRawData.zip"
    update_frequency: "daily"
    display_name: "Application for Permit to Drill"
  production_data:
    url: "https://www.data.bsee.gov/Production/Files/ProductionRawData.zip" 
    update_frequency: "bi_monthly"
    display_name: "Production Data"
  war_data:
    url: "https://www.data.bsee.gov/Well/Files/eWellWARRawData.zip"
    update_frequency: "daily"
    display_name: "eWell Submissions WAR"

# From src/worldenergydata/base_configs/modules/bsee/bsee.yml
filepaths:
  zip: "data/modules/bsee/zip"    # Existing (may not be used if in-memory)
  bin: "data/modules/bsee/bin"    # Existing output directory
  
# New API research configuration
api_research:
  enabled: true
  fallback_to_scraping: true
  main_portal: "https://www.data.bsee.gov/Main/RawData.aspx"
```

## Security Considerations

- **Input Validation:** Sanitize all user inputs and date ranges
- **Rate Limiting:** Respect BSEE website limits to avoid IP blocking
- **Error Handling:** Never expose internal paths or sensitive configs in errors
- **Data Integrity:** Verify checksums for downloaded files
- **Access Control:** Use read-only file permissions for binary outputs

## Testing Strategy

- **Unit Tests:** Mock all external data sources
- **Integration Tests:** Test with sample BSEE data files
- **Performance Tests:** Benchmark against current implementation
- **Resilience Tests:** Simulate network failures and corrupted data
- **End-to-End Tests:** Full refresh cycle with real data (in test environment)