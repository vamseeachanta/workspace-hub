---
name: web-scraper-energy
description: Web Scraper Energy (user)
capabilities: []
requires: []
see_also: []
---

# Web Scraper Energy Skill

> Web scraping workflows for energy data collection using Scrapy and BeautifulSoup

## When to Use This Skill

Use this skill when you need to:
- Scrape BSEE/BOEM websites for data not in APIs
- Collect lease sale results and bid data
- Extract platform and facility information
- Build automated data collection pipelines
- Parse HTML tables into structured data

## Core Pattern

```python
"""
ABOUTME: Web scraping utilities for energy data collection
ABOUTME: Supports Scrapy spiders and BeautifulSoup parsing
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import requests
import time


@dataclass
class ScrapingConfig:
    """Configuration for web scraping."""
    base_url: str
    rate_limit_sec: float = 1.0
    max_retries: int = 3
    timeout_sec: int = 30
    user_agent: str = "WorldEnergyData/1.0"
    cache_enabled: bool = True


class BOEMScraper:
    """
    Scraper for BOEM (Bureau of Ocean Energy Management) data.

    Targets:
    - Lease sale results
    - Platform/facility data
    - Environmental studies
    """

    def __init__(self, config: Optional[ScrapingConfig] = None):
        self.config = config or ScrapingConfig(
            base_url="https://www.boem.gov"
        )
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.config.user_agent
        })

    def _fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a page with rate limiting."""
        time.sleep(self.config.rate_limit_sec)

        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(
                    url,
                    timeout=self.config.timeout_sec
                )
                response.raise_for_status()
                return BeautifulSoup(response.text, "html.parser")
            except requests.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)

    def get_lease_sale_results(self, sale_number: int) -> List[Dict]:
        """
        Extract lease sale bid results.

        Returns list of winning bids with block, company, amount.
        """
        url = f"{self.config.base_url}/oil-gas-energy/leasing/lease-sales"
        soup = self._fetch_page(url)

        # Find the specific sale results table
        results = []
        tables = soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]

            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 4:
                    results.append({
                        "block": cells[0].get_text(strip=True),
                        "area": cells[1].get_text(strip=True),
                        "company": cells[2].get_text(strip=True),
                        "bid_amount": self._parse_currency(cells[3].get_text(strip=True))
                    })

        return results

    def get_platform_data(self, area_code: str = "GC") -> List[Dict]:
        """
        Extract platform/structure data for an area.

        Returns list of platforms with name, type, water depth.
        """
        url = f"{self.config.base_url}/oil-gas-energy/platforms"
        soup = self._fetch_page(url)

        platforms = []
        # Parse platform listing tables
        for item in soup.select(".platform-item"):
            platforms.append({
                "name": item.select_one(".platform-name").get_text(strip=True),
                "type": item.select_one(".platform-type").get_text(strip=True),
                "area": item.select_one(".platform-area").get_text(strip=True),
                "block": item.select_one(".platform-block").get_text(strip=True),
                "water_depth_ft": self._parse_number(
                    item.select_one(".water-depth").get_text(strip=True)
                )
            })

        return [p for p in platforms if p["area"] == area_code]

    def _parse_currency(self, text: str) -> float:
        """Parse currency string to float."""
        import re
        clean = re.sub(r"[,$]", "", text)
        try:
            return float(clean)
        except ValueError:
            return 0.0

    def _parse_number(self, text: str) -> float:
        """Parse number from text."""
        import re
        match = re.search(r"[\d,]+\.?\d*", text)
        if match:
            return float(match.group().replace(",", ""))
        return 0.0


class BSEETableScraper:
    """
    Scraper for BSEE HTML tables.

    For data not available via BSEE Data Center APIs.
    """

    def __init__(self):
        self.session = requests.Session()

    def scrape_production_table(
        self,
        url: str,
        date_col: str = "Date",
        value_cols: List[str] = None
    ) -> List[Dict]:
        """
        Scrape production data from HTML table.

        Args:
            url: Page URL containing table
            date_col: Column name for date
            value_cols: Columns to extract

        Returns:
            List of row dictionaries
        """
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table")
        if not table:
            return []

        # Extract headers
        headers = []
        header_row = table.find("tr")
        for th in header_row.find_all(["th", "td"]):
            headers.append(th.get_text(strip=True))

        # Extract data rows
        data = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) == len(headers):
                row_dict = {}
                for i, cell in enumerate(cells):
                    row_dict[headers[i]] = cell.get_text(strip=True)
                data.append(row_dict)

        return data


class DataValidator:
    """Validate scraped data quality."""

    @staticmethod
    def validate_production(data: List[Dict]) -> List[str]:
        """Check production data for issues."""
        issues = []

        for i, row in enumerate(data):
            # Check for missing values
            if not row.get("date"):
                issues.append(f"Row {i}: Missing date")

            # Check for negative values
            for key in ["oil_bbl", "gas_mcf"]:
                if key in row:
                    try:
                        val = float(row[key])
                        if val < 0:
                            issues.append(f"Row {i}: Negative {key}")
                    except (ValueError, TypeError):
                        issues.append(f"Row {i}: Invalid {key} value")

        return issues
```

## YAML Configuration Template

```yaml
# config/input/scraping-config.yaml

metadata:
  feature_name: "energy-scraping"
  created: "2025-01-15"

scraping:
  rate_limit_sec: 1.5
  max_retries: 3
  timeout_sec: 30
  cache_enabled: true
  cache_ttl_hours: 24

targets:
  - name: "lease_sales"
    source: "boem"
    sale_numbers: [257, 258, 259]
    output: "data/lease_sales/"

  - name: "platforms"
    source: "boem"
    areas: ["GC", "WR", "MC"]
    output: "data/platforms/"

validation:
  enabled: true
  fail_on_errors: false
  log_warnings: true

output:
  format: "csv"
  include_metadata: true
```

## CLI Usage

```bash
# Scrape lease sale results
python -m worldenergydata.scraper \
    --source boem \
    --type lease-sale \
    --sale 259 \
    --output data/lease_sale_259.csv

# Scrape platform data
python -m worldenergydata.scraper \
    --source boem \
    --type platforms \
    --area GC \
    --output data/gc_platforms.csv
```

## Best Practices

1. **Respect rate limits** - Use 1-2 second delays between requests
2. **Cache responses** - Avoid re-fetching unchanged data
3. **Validate data** - Check for missing/invalid values post-scrape
4. **Handle errors** - Implement retries with exponential backoff
5. **User agent** - Identify your scraper appropriately
6. **Check robots.txt** - Respect site crawling policies
