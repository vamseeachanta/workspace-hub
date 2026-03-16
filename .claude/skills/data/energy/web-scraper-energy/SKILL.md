---
name: web-scraper-energy
description: Web scraping workflows for energy data collection from BSEE and BOEM
  using Scrapy
capabilities: []
requires: []
see_also:
- web-scraper-energy-best-practices
tags: []
category: data
version: 1.0.0
---

# Web Scraper Energy

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

*See sub-skills for full details.*

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


*See sub-skills for full details.*

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

## Web Crawling & MCP Assessment (2026-03-14)

**No external MCP or paid service needed for energy data scraping.**

This skill's `requests` + `BeautifulSoup` pattern is sufficient for BSEE/BOEM/EIA targets.
For async fetching at scale (WRK-1202 Tier 3), upgrade to `httpx` (async) + `beautifulsoup4`.
For JS-rendered pages, use `claude-in-chrome` browser automation (already available).
See `doc-research-download` skill for the full assessment.

## Sub-Skills

- [Best Practices](best-practices/SKILL.md)
