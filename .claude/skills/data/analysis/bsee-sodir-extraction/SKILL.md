---
name: bsee-sodir-extraction
version: 1.0.0
description: Extract and process energy data from BSEE (Gulf of Mexico) and SODIR
  (Norway) regulatory databases
author: workspace-hub
category: data-analysis
tags:
- bsee
- sodir
- energy-data
- oil-gas
- offshore
- web-scraping
- api
platforms:
- python
capabilities: []
requires: []
see_also:
- bsee-sodir-extraction-1-bsee-data-extraction
- bsee-sodir-extraction-2-sodirnpd-data-extraction-norway
- bsee-sodir-extraction-3-combined-analysis
- bsee-sodir-extraction-4-npv-analysis-with-regulatory-data
- bsee-sodir-extraction-1-rate-limiting
scripts_exempt: true
---

# Bsee Sodir Extraction

## When to Use This Skill

Use BSEE/SODIR data extraction when you need:
- **Production data** - Oil, gas, water production by field/well
- **Well information** - Directional surveys, completions, drilling data
- **Field data** - Reserves, operators, development status
- **HSE data** - Safety incidents, environmental compliance
- **Economic analysis** - NPV calculations using regulatory data
- **Regulatory compliance** - Track permits, violations, inspections

**Data sources covered:**
- **BSEE (US Gulf of Mexico)**: Production, wells, platforms, safety
- **SODIR (Norway)**: Fields, production, wells, discoveries
- **NPD FactPages**: Norwegian petroleum data (legacy)

## Complete Pipeline Example

```python
"""
Complete BSEE/SODIR data extraction and analysis pipeline.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go


def run_extraction_pipeline(
    output_dir: Path = Path("data"),
    report_dir: Path = Path("reports")
) -> dict:
    """
    Run complete data extraction and analysis pipeline.

    Returns:
        Dictionary with extraction summary
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "extraction_date": datetime.now().isoformat(),

*See sub-skills for full details.*

## Resources

- **BSEE Data Center**: https://www.data.bsee.gov/
- **SODIR FactPages**: https://factpages.sodir.no/
- **BSEE API Documentation**: https://www.data.bsee.gov/api-documentation
- **NPD (legacy)**: https://www.npd.no/en/facts/

---

**Use this skill for all energy regulatory data extraction in worldenergydata!**

## Sub-Skills

- [1. BSEE Data Extraction](1-bsee-data-extraction/SKILL.md)
- [2. SODIR/NPD Data Extraction (Norway)](2-sodirnpd-data-extraction-norway/SKILL.md)
- [3. Combined Analysis](3-combined-analysis/SKILL.md)
- [4. NPV Analysis with Regulatory Data](4-npv-analysis-with-regulatory-data/SKILL.md)
- [1. Rate Limiting (+2)](1-rate-limiting/SKILL.md)
