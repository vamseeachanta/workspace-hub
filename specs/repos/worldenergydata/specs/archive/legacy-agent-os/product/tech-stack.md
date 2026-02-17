# Technical Stack

> Last Updated: 2026-01-08
> Version: 1.1.0

## Core Technologies

### Application Framework
- **Framework:** Python Package Library
- **Version:** 3.9+
- **Package Manager:** UV (modern Python package manager)

### Database
- **Primary:** File-based (CSV, Excel, YAML)
- **Version:** n/a
- **Processing:** Pandas DataFrames

## Development Stack

### Language and Runtime
- **Language:** Python
- **Version:** 3.9+
- **Package Manager:** UV
- **Build System:** pyproject.toml with setuptools backend

### Data Processing
- **Core Libraries:** pandas, numpy, numpy-financial
- **HSE Data Processing:** BSEE incident databases integration, safety metrics calculation, operational risk scoring, ESG compliance reporting
- **File Formats:** openpyxl, xlrd, xmltodict, pyyaml
- **Date/Time:** python-dateutil, pytz, tzdata

### Web Scraping and APIs
- **Framework:** Scrapy 2.12.0
- **Browser Automation:** Selenium
- **HTTP Requests:** requests, urllib3
- **HTML Parsing:** BeautifulSoup4 (bs4)
- **Async Support:** trio, trio-websocket

### Visualization
- **Plotting Libraries:** matplotlib, plotly
- **Web Graphics:** HTML exports, interactive charts

## Development Tools

### Code Quality
- **Formatter:** black (>= 23.0)
- **Import Sorting:** isort (>= 5.0.0)
- **Linting:** ruff (>= 0.12.3)
- **Type Checking:** mypy (>= 1.4.1)

### Testing
- **Testing Framework:** pytest (>= 7.0.0)
- **Comparison Tools:** deepdiff (>= 6.0.0)
- **Legacy Support:** assetutilities for existing tests

### Version Management
- **Version Bumping:** bumpver (>= 2023.1129)
- **Build Tools:** build (>= 1.0.0)
- **Publishing:** twine (>= 1.0.0)

## Infrastructure

### Application Hosting
- **Platform:** Local development/deployment
- **Service:** Python package distribution via PyPI
- **Region:** Global (PyPI CDN)

### Data Storage
- **Provider:** Local file system
- **Service:** CSV, Excel, YAML file storage
- **Backups:** Git version control

### Asset Storage
- **Provider:** Local file system / Git LFS
- **Service:** Large data files in data/ directory
- **Access:** Direct file system access

## Deployment

### CI/CD Pipeline
- **Platform:** GitHub Actions (planned)
- **Trigger:** Push to main branch
- **Tests:** pytest suite execution

### Environments
- **Production:** PyPI package releases
- **Development:** Local UV environment
- **Testing:** pytest with GitHub Actions

### Package Distribution
- **Registry:** PyPI (Python Package Index)
- **Format:** wheel (.whl) and source distribution (.tar.gz)
- **Installation:** pip install worldenergydata or uv add worldenergydata

## Configuration Management

### Configuration Format
- **Primary:** YAML files
- **Location:** User-defined input files
- **Validation:** Custom validation in engine.py

### Environment Management
- **Tool:** UV for dependency management
- **Files:** pyproject.toml, uv.lock
- **Environment:** Isolated virtual environments per project