# WorldEnergyData Skills Enhancement Plan

## Summary

Review of the worldenergydata repository mission and proposal for additional Claude Code skills to enhance development productivity in the energy data analysis domain.

## Current State

### Existing Skills (2)
1. **bsee-data-extractor** - BSEE production data extraction, caching, normalization
2. **npv-analyzer** - NPV calculation, cash flow modeling, scenario analysis

### Repository Capabilities (from mission.md)
- BSEE data integration ✓ (covered)
- SODIR (Norwegian) data extraction (NOT covered)
- NPV/economic analysis ✓ (covered)
- Production forecasting & decline curves (partially covered)
- Web scraping (Scrapy, Selenium, BeautifulSoup) (NOT covered)
- Field-specific analysis (Anchor, Julia, Jack, St. Malo) (NOT covered)
- Data visualization (matplotlib, plotly) (NOT covered)
- YAML-based configuration (partially covered)
- Wind energy databases (NOT covered)
- Validation framework (NOT covered)

---

## Proposed New Skills (5)

### 1. production-forecaster
**Purpose:** Production curve analysis, decline modeling, and forecasting

**Justification:** The mission mentions production forecasting as a key capability. The codebase has modules for production analysis but no dedicated skill.

**Key Features:**
- Arps decline curve fitting (exponential, hyperbolic, harmonic)
- Type curve generation from historical data
- Production forecast generation
- Uncertainty quantification (P10/P50/P90)
- Integration with BSEE historical data

**Files to leverage:**
- `modules/bsee/analysis/production_api10.py`
- `modules/bsee/analysis/well_api10.py`
- `modules/bsee/analysis/well_api12.py`

---

### 2. sodir-data-extractor
**Purpose:** Extract and process Norwegian Petroleum Directorate (SODIR) data

**Justification:** Mission explicitly mentions SODIR as a data source, but no skill exists.

**Key Features:**
- Norwegian continental shelf field data extraction
- Production data normalization (similar to BSEE)
- Field-level aggregation
- Cross-comparison with GOM fields
- Data caching and refresh

**Pattern:** Mirror the bsee-data-extractor structure for consistency

---

### 3. energy-data-visualizer
**Purpose:** Interactive visualization for oil & gas data analysis

**Justification:** Mission emphasizes matplotlib and plotly. The existing skills mention report generation but lack a dedicated visualization skill.

**Key Features:**
- Production plot templates (time series, decline curves)
- Field comparison charts
- Economic scenario waterfall charts
- Interactive HTML dashboards
- Map-based visualizations (GOM blocks)
- Export to multiple formats (HTML, PNG, PDF)

**Libraries:** Plotly (primary), matplotlib (static), folium (maps)

---

### 4. field-analyzer
**Purpose:** Deepwater field-specific analysis for major developments

**Justification:** Mission specifically mentions Anchor, Julia, Jack, St. Malo fields as analysis targets.

**Key Features:**
- Field-specific configuration templates
- Multi-well aggregation by field
- Development type analysis (FPSO, subsea, TLP)
- Field economics comparison
- Lease/block grouping by field name
- Historical performance tracking

**Fields to support:** Lower Tertiary (Anchor, Jack, St. Malo, Julia), and extensible to others

---

### 5. web-scraper-energy
**Purpose:** Web scraping workflows for energy data collection

**Justification:** Mission lists Scrapy, Selenium, BeautifulSoup as technologies. Codebase has legacy scrapy modules.

**Key Features:**
- Scrapy spider templates for BSEE/BOEM websites
- Selenium automation for dynamic pages
- BeautifulSoup parsing utilities
- Rate limiting and polite scraping
- Data validation post-scrape
- Caching and incremental updates

**Files to leverage:**
- `modules/bsee/data/_legacy/scrapy_block_data.py`
- `modules/bsee/data/_legacy/scrapy_production_data.py`
- `modules/bsee/data/_legacy/beautifulSoup_API.py`

---

## Implementation Priority

| Skill | Priority | Effort | Value |
|-------|----------|--------|-------|
| production-forecaster | High | Medium | High - Core analysis capability |
| sodir-data-extractor | Medium | Medium | Medium - Expands data sources |
| energy-data-visualizer | High | Low | High - Immediate usability |
| field-analyzer | Medium | Medium | Medium - Domain-specific value |
| web-scraper-energy | Low | High | Low - Legacy code needs update |

---

## File Structure

```
worldenergydata/.claude/skills/
├── bsee-data-extractor/      # Existing
│   └── SKILL.md
├── npv-analyzer/             # Existing
│   └── SKILL.md
├── production-forecaster/    # NEW
│   └── SKILL.md
├── sodir-data-extractor/     # NEW
│   └── SKILL.md
├── energy-data-visualizer/   # NEW
│   └── SKILL.md
├── field-analyzer/           # NEW
│   └── SKILL.md
└── web-scraper-energy/       # NEW
    └── SKILL.md
```

---

## Next Steps

1. Create each SKILL.md file with:
   - YAML frontmatter (name, description)
   - When to Use section
   - Core Pattern
   - Implementation code examples
   - YAML configuration templates
   - CLI usage examples
   - Best practices

2. Update workspace-hub skills README.md to list new worldenergydata skills

3. Test skills with sample workflows

---

## Critical Files

- **Mission reference:** `/mnt/github/workspace-hub/worldenergydata/.agent-os/product/mission.md`
- **Existing skills:** `/mnt/github/workspace-hub/worldenergydata/.claude/skills/`
- **Source modules:** `/mnt/github/workspace-hub/worldenergydata/src/worldenergydata/modules/`
- **Skills README:** `/mnt/github/workspace-hub/.claude/skills/README.md`
