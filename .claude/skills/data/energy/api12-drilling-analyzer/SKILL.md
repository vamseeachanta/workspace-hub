---
name: api12-drilling-analyzer
description: Analyze drilling performance and metrics using API 12-digit well numbering system. Use for drilling time analysis, cost benchmarking, well comparison, sidetracks tracking, and drilling efficiency metrics across GOM fields.
capabilities: []
requires: []
see_also: []
---

# API12 Drilling Analyzer

Comprehensive drilling analysis using the API (American Petroleum Institute) 12-digit well identification system for Gulf of Mexico wells.

## When to Use

- Parsing and validating API well numbers (10, 12, or 14 digit formats)
- Analyzing drilling performance by operator, field, or area
- Benchmarking drilling times and costs across similar wells
- Tracking sidetrack wells and their relationship to parent bores
- Calculating drilling efficiency metrics (ROP, NPT, connection time)
- Comparing deepwater vs. shelf drilling performance
- Identifying drilling hazards by area/block
- Generating drilling AFE (Authorization for Expenditure) estimates

## Core Pattern

```
API Number → Parse/Validate → Query BSEE Data → Analyze Drilling Metrics → Benchmark → Report
```

### API Number Structure

| Digits | Description | Example |
|--------|-------------|---------|
| 1-2 | State Code | 17 = Louisiana (OCS) |
| 3-5 | County/Area Code | 710 = Green Canyon |
| 6-10 | Well Sequence | 49130 |
| 11-12 | Sidetrack Number | 00, 01, 02 |
| 13-14 | Completion Number | 00, 01 (14-digit only) |

## Implementation

### Data Models

```python
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import pandas as pd
import re

class APIFormat(Enum):
    """API number format types."""
    API_10 = "api_10"  # State + County + Well
    API_12 = "api_12"  # + Sidetrack
    API_14 = "api_14"  # + Completion

class WellType(Enum):
    """Well classification types."""
    EXPLORATION = "exploration"
    DEVELOPMENT = "development"
    INJECTION = "injection"
    DISPOSAL = "disposal"
    OBSERVATION = "observation"

class HoleSection(Enum):
    """Wellbore sections."""
    CONDUCTOR = "conductor"
    SURFACE = "surface"
    INTERMEDIATE = "intermediate"
    PRODUCTION = "production"
    LINER = "liner"

@dataclass
class APINumber:
    """
    Parsed API well number with validation.

    The API number uniquely identifies wells in US oil and gas operations.
    """
    raw: str
    state_code: str = ""
    county_code: str = ""
    well_sequence: str = ""
    sidetrack: str = "00"
    completion: str = "00"

    def __post_init__(self):
        """Parse and validate API number."""
        # Remove any non-numeric characters
        cleaned = re.sub(r'[^0-9]', '', self.raw)

        if len(cleaned) >= 10:
            self.state_code = cleaned[0:2]
            self.county_code = cleaned[2:5]
            self.well_sequence = cleaned[5:10]

        if len(cleaned) >= 12:
            self.sidetrack = cleaned[10:12]

        if len(cleaned) >= 14:
            self.completion = cleaned[12:14]

    @property
    def format_type(self) -> APIFormat:
        """Determine API format based on length."""
        length = len(re.sub(r'[^0-9]', '', self.raw))
        if length >= 14:
            return APIFormat.API_14
        elif length >= 12:
            return APIFormat.API_12
        return APIFormat.API_10

    @property
    def api_10(self) -> str:
        """Return 10-digit API number."""
        return f"{self.state_code}{self.county_code}{self.well_sequence}"

    @property
    def api_12(self) -> str:
        """Return 12-digit API number."""
        return f"{self.api_10}{self.sidetrack}"

    @property
    def api_14(self) -> str:
        """Return 14-digit API number."""
        return f"{self.api_12}{self.completion}"

    @property
    def is_sidetrack(self) -> bool:
        """Check if well is a sidetrack."""
        return self.sidetrack != "00"

    @property
    def sidetrack_number(self) -> int:
        """Get sidetrack number as integer."""
        return int(self.sidetrack)

    @property
    def parent_api(self) -> str:
        """Get parent well API (sidetrack 00)."""
        return f"{self.api_10}00"

    def is_valid(self) -> bool:
        """Validate API number format."""
        # Check minimum length
        if len(self.api_10) != 10:
            return False
        # Check state code is valid (17 = Louisiana OCS, etc.)
        valid_states = {'17', '42', '48', '01', '28'}  # Common GOM states
        return self.state_code in valid_states or int(self.state_code) > 0

@dataclass
class DrillingPhase:
    """Single drilling phase record."""
    hole_section: HoleSection
    start_date: date
    end_date: Optional[date] = None
    start_depth_ft: float = 0.0
    end_depth_ft: float = 0.0
    hole_size_in: Optional[float] = None
    casing_size_in: Optional[float] = None
    mud_weight_ppg: Optional[float] = None

    @property
    def duration_days(self) -> Optional[float]:
        """Calculate phase duration in days."""
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days
        return None

    @property
    def footage_drilled(self) -> float:
        """Calculate footage drilled in this phase."""
        return self.end_depth_ft - self.start_depth_ft

    @property
    def avg_rop(self) -> Optional[float]:
        """Calculate average ROP (ft/hr) assuming 24hr/day."""
        duration = self.duration_days
        if duration and duration > 0:
            return self.footage_drilled / (duration * 24)
        return None

@dataclass
class DrillingRecord:
    """Complete drilling record for a well."""
    api: APINumber
    well_name: Optional[str] = None
    operator: Optional[str] = None
    well_type: WellType = WellType.EXPLORATION
    rig_name: Optional[str] = None
    spud_date: Optional[date] = None
    td_date: Optional[date] = None
    release_date: Optional[date] = None
    water_depth_ft: float = 0.0
    total_depth_md_ft: float = 0.0
    total_depth_tvd_ft: float = 0.0
    target_formation: Optional[str] = None
    phases: List[DrillingPhase] = field(default_factory=list)

    # Cost metrics
    drilling_cost_usd: Optional[float] = None
    completion_cost_usd: Optional[float] = None
    daily_rig_rate_usd: Optional[float] = None

    # Time metrics
    total_drilling_days: Optional[float] = None
    productive_time_pct: Optional[float] = None
    npt_days: Optional[float] = None  # Non-Productive Time

    @property
    def is_deepwater(self) -> bool:
        """Check if well is deepwater (>1000ft water depth)."""
        return self.water_depth_ft > 1000

    @property
    def is_ultra_deepwater(self) -> bool:
        """Check if well is ultra-deepwater (>5000ft)."""
        return self.water_depth_ft > 5000

    @property
    def drilling_duration(self) -> Optional[int]:
        """Calculate drilling duration from spud to TD."""
        if self.spud_date and self.td_date:
            return (self.td_date - self.spud_date).days
        return None

    @property
    def total_rig_time(self) -> Optional[int]:
        """Calculate total rig time from spud to release."""
        if self.spud_date and self.release_date:
            return (self.release_date - self.spud_date).days
        return None

    @property
    def overall_rop(self) -> Optional[float]:
        """Calculate overall average ROP (ft/hr)."""
        duration = self.drilling_duration
        if duration and duration > 0 and self.total_depth_md_ft > 0:
            return self.total_depth_md_ft / (duration * 24)
        return None

    @property
    def cost_per_foot(self) -> Optional[float]:
        """Calculate drilling cost per foot."""
        if self.drilling_cost_usd and self.total_depth_md_ft > 0:
            return self.drilling_cost_usd / self.total_depth_md_ft
        return None

    @property
    def npt_percentage(self) -> Optional[float]:
        """Calculate NPT as percentage of total time."""
        if self.npt_days and self.total_rig_time:
            return (self.npt_days / self.total_rig_time) * 100
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame."""
        return {
            'api_12': self.api.api_12,
            'api_10': self.api.api_10,
            'sidetrack': self.api.sidetrack,
            'is_sidetrack': self.api.is_sidetrack,
            'well_name': self.well_name,
            'operator': self.operator,
            'well_type': self.well_type.value,
            'rig_name': self.rig_name,
            'spud_date': self.spud_date,
            'td_date': self.td_date,
            'release_date': self.release_date,
            'water_depth_ft': self.water_depth_ft,
            'total_depth_md_ft': self.total_depth_md_ft,
            'total_depth_tvd_ft': self.total_depth_tvd_ft,
            'target_formation': self.target_formation,
            'is_deepwater': self.is_deepwater,
            'is_ultra_deepwater': self.is_ultra_deepwater,
            'drilling_duration_days': self.drilling_duration,
            'total_rig_time_days': self.total_rig_time,
            'overall_rop_ft_hr': self.overall_rop,
            'drilling_cost_usd': self.drilling_cost_usd,
            'cost_per_foot': self.cost_per_foot,
            'npt_days': self.npt_days,
            'npt_percentage': self.npt_percentage
        }
```

### Drilling Analyzer

```python
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class DrillingAnalyzer:
    """
    Analyze drilling performance using API-identified wells.

    Provides benchmarking, comparison, and performance metrics
    for Gulf of Mexico drilling operations.
    """

    # Area code to name mapping (GOM OCS)
    AREA_CODES = {
        '710': 'Green Canyon',
        '759': 'Walker Ridge',
        '607': 'Mississippi Canyon',
        '687': 'Keathley Canyon',
        '651': 'Garden Banks',
        '703': 'Alaminos Canyon',
        '695': 'Atwater Valley',
        '735': 'DeSoto Canyon'
    }

    def __init__(self, records: List[DrillingRecord] = None):
        """
        Initialize drilling analyzer.

        Args:
            records: List of DrillingRecord objects
        """
        self.records = records or []
        self._df = None

    @property
    def dataframe(self) -> pd.DataFrame:
        """Get records as DataFrame."""
        if self._df is None and self.records:
            self._df = pd.DataFrame([r.to_dict() for r in self.records])
        return self._df

    def add_record(self, record: DrillingRecord):
        """Add a drilling record."""
        self.records.append(record)
        self._df = None  # Reset cached DataFrame

    def parse_api(self, api_string: str) -> APINumber:
        """
        Parse an API number string.

        Args:
            api_string: API number in any format

        Returns:
            APINumber object with parsed components
        """
        return APINumber(raw=api_string)

    def get_area_name(self, api: APINumber) -> str:
        """Get area name from API county code."""
        return self.AREA_CODES.get(api.county_code, f"Area {api.county_code}")

    def find_sidetracks(self, api_10: str) -> List[DrillingRecord]:
        """
        Find all sidetracks for a parent well.

        Args:
            api_10: 10-digit API number of parent well

        Returns:
            List of DrillingRecords including parent and sidetracks
        """
        return [r for r in self.records if r.api.api_10 == api_10]

    def benchmark_by_area(self) -> pd.DataFrame:
        """
        Benchmark drilling performance by area.

        Returns:
            DataFrame with area-level statistics
        """
        df = self.dataframe
        if df is None or df.empty:
            return pd.DataFrame()

        # Extract area from API
        df['area_code'] = df['api_10'].str[2:5]
        df['area_name'] = df['area_code'].map(self.AREA_CODES)

        return df.groupby('area_name').agg({
            'api_12': 'count',
            'drilling_duration_days': ['mean', 'std', 'min', 'max'],
            'total_depth_md_ft': ['mean', 'std', 'min', 'max'],
            'water_depth_ft': ['mean', 'min', 'max'],
            'overall_rop_ft_hr': ['mean', 'std'],
            'cost_per_foot': ['mean', 'std'],
            'npt_percentage': ['mean', 'std']
        }).round(2)

    def benchmark_by_operator(self) -> pd.DataFrame:
        """
        Benchmark drilling performance by operator.

        Returns:
            DataFrame with operator-level statistics
        """
        df = self.dataframe
        if df is None or df.empty:
            return pd.DataFrame()

        return df.groupby('operator').agg({
            'api_12': 'count',
            'drilling_duration_days': ['mean', 'std'],
            'total_depth_md_ft': ['mean', 'max'],
            'overall_rop_ft_hr': ['mean'],
            'cost_per_foot': ['mean'],
            'npt_percentage': ['mean']
        }).round(2).rename(columns={'api_12': 'well_count'})

    def benchmark_by_water_depth(self, bins: List[int] = None) -> pd.DataFrame:
        """
        Benchmark by water depth category.

        Args:
            bins: Water depth bin edges (default: shelf, deepwater, ultra-deepwater)

        Returns:
            DataFrame with depth-category statistics
        """
        df = self.dataframe
        if df is None or df.empty:
            return pd.DataFrame()

        bins = bins or [0, 400, 1000, 5000, 15000]
        labels = ['Shelf (<400ft)', 'Deepwater (400-1000ft)',
                  'Deep (1000-5000ft)', 'Ultra-Deep (>5000ft)']

        df['depth_category'] = pd.cut(df['water_depth_ft'], bins=bins, labels=labels)

        return df.groupby('depth_category').agg({
            'api_12': 'count',
            'drilling_duration_days': ['mean', 'std'],
            'overall_rop_ft_hr': ['mean'],
            'cost_per_foot': ['mean'],
            'npt_percentage': ['mean']
        }).round(2)

    def find_similar_wells(self, target: DrillingRecord,
                          max_depth_diff: float = 2000,
                          max_wd_diff: float = 500,
                          max_results: int = 10) -> pd.DataFrame:
        """
        Find wells similar to target for benchmarking.

        Args:
            target: Target well to compare
            max_depth_diff: Maximum total depth difference (ft)
            max_wd_diff: Maximum water depth difference (ft)
            max_results: Maximum number of results

        Returns:
            DataFrame of similar wells
        """
        df = self.dataframe
        if df is None or df.empty:
            return pd.DataFrame()

        # Filter by similar characteristics
        similar = df[
            (abs(df['total_depth_md_ft'] - target.total_depth_md_ft) <= max_depth_diff) &
            (abs(df['water_depth_ft'] - target.water_depth_ft) <= max_wd_diff) &
            (df['api_12'] != target.api.api_12)  # Exclude target well
        ].copy()

        # Calculate similarity score
        similar['depth_diff'] = abs(similar['total_depth_md_ft'] - target.total_depth_md_ft)
        similar['wd_diff'] = abs(similar['water_depth_ft'] - target.water_depth_ft)
        similar['similarity_score'] = similar['depth_diff'] + similar['wd_diff']

        return similar.sort_values('similarity_score').head(max_results)

    def calculate_afe_estimate(self, target: DrillingRecord,
                               confidence_level: float = 0.8) -> Dict:
        """
        Estimate AFE (Authorization for Expenditure) based on similar wells.

        Args:
            target: Target well for AFE
            confidence_level: Percentile for high estimate (default P80)

        Returns:
            Dictionary with AFE estimates
        """
        similar = self.find_similar_wells(target)

        if similar.empty:
            return {'error': 'No similar wells found for benchmarking'}

        durations = similar['drilling_duration_days'].dropna()
        costs = similar['drilling_cost_usd'].dropna()

        result = {
            'well': target.api.api_12,
            'similar_wells_count': len(similar),
            'duration_estimate_days': {
                'p10': durations.quantile(0.1) if len(durations) > 0 else None,
                'p50': durations.quantile(0.5) if len(durations) > 0 else None,
                'p90': durations.quantile(0.9) if len(durations) > 0 else None,
                'mean': durations.mean() if len(durations) > 0 else None
            }
        }

        if len(costs) > 0:
            result['cost_estimate_usd'] = {
                'p10': costs.quantile(0.1),
                'p50': costs.quantile(0.5),
                'p90': costs.quantile(0.9),
                'mean': costs.mean()
            }

        # Estimate based on rig rate if available
        if target.daily_rig_rate_usd and result['duration_estimate_days']['p50']:
            spread_cost = target.daily_rig_rate_usd * result['duration_estimate_days']['p50']
            result['estimated_spread_cost'] = spread_cost

        return result

    def drilling_efficiency_metrics(self) -> pd.DataFrame:
        """
        Calculate drilling efficiency metrics across all wells.

        Returns:
            DataFrame with efficiency metrics
        """
        df = self.dataframe
        if df is None or df.empty:
            return pd.DataFrame()

        metrics = []
        for record in self.records:
            if record.drilling_duration and record.total_depth_md_ft > 0:
                metrics.append({
                    'api_12': record.api.api_12,
                    'operator': record.operator,
                    'footage_per_day': record.total_depth_md_ft / record.drilling_duration,
                    'rop_ft_hr': record.overall_rop,
                    'productive_time_pct': record.productive_time_pct,
                    'npt_pct': record.npt_percentage,
                    'cost_efficiency': record.cost_per_foot,
                    'water_depth_ft': record.water_depth_ft,
                    'total_depth_ft': record.total_depth_md_ft
                })

        return pd.DataFrame(metrics)

    def sidetrack_analysis(self) -> pd.DataFrame:
        """
        Analyze sidetrack patterns and performance.

        Returns:
            DataFrame comparing original bores to sidetracks
        """
        df = self.dataframe
        if df is None or df.empty:
            return pd.DataFrame()

        # Group by parent API
        parent_groups = df.groupby('api_10')

        results = []
        for api_10, group in parent_groups:
            original = group[~group['is_sidetrack']].iloc[0] if any(~group['is_sidetrack']) else None
            sidetracks = group[group['is_sidetrack']]

            results.append({
                'parent_api': api_10,
                'original_well': True if original is not None else False,
                'num_sidetracks': len(sidetracks),
                'original_td_ft': original['total_depth_md_ft'] if original is not None else None,
                'avg_sidetrack_td_ft': sidetracks['total_depth_md_ft'].mean() if not sidetracks.empty else None,
                'original_duration_days': original['drilling_duration_days'] if original is not None else None,
                'avg_sidetrack_duration': sidetracks['drilling_duration_days'].mean() if not sidetracks.empty else None
            })

        return pd.DataFrame(results)
```

### Report Generator

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

class DrillingReportGenerator:
    """Generate interactive drilling analysis reports."""

    def __init__(self, analyzer: DrillingAnalyzer):
        """
        Initialize report generator.

        Args:
            analyzer: DrillingAnalyzer with drilling data
        """
        self.analyzer = analyzer

    def generate_benchmark_report(self, output_path: Path, title: str = "Drilling Benchmark"):
        """
        Generate comprehensive drilling benchmark report.

        Args:
            output_path: Path for HTML output
            title: Report title
        """
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Drilling Duration by Area',
                'ROP Distribution by Water Depth',
                'Operator Performance Comparison',
                'NPT Analysis',
                'Cost per Foot Trend',
                'Sidetrack vs Original Performance'
            ),
            vertical_spacing=0.08
        )

        df = self.analyzer.dataframe

        # 1. Drilling Duration by Area
        area_stats = self.analyzer.benchmark_by_area()
        if not area_stats.empty:
            areas = area_stats.index.tolist()
            durations = area_stats[('drilling_duration_days', 'mean')].values

            fig.add_trace(
                go.Bar(x=areas, y=durations, name='Avg Duration (days)',
                       marker_color='steelblue'),
                row=1, col=1
            )

        # 2. ROP by Water Depth
        if 'water_depth_ft' in df.columns and 'overall_rop_ft_hr' in df.columns:
            fig.add_trace(
                go.Scatter(x=df['water_depth_ft'], y=df['overall_rop_ft_hr'],
                          mode='markers', name='ROP',
                          marker=dict(color='green', size=8)),
                row=1, col=2
            )

        # 3. Operator Comparison
        op_stats = self.analyzer.benchmark_by_operator()
        if not op_stats.empty:
            operators = op_stats.index[:10].tolist()  # Top 10
            well_counts = op_stats[('api_12', 'count')].head(10).values

            fig.add_trace(
                go.Bar(x=operators, y=well_counts, name='Well Count',
                       marker_color='orange'),
                row=2, col=1
            )

        # 4. NPT Analysis
        if 'npt_percentage' in df.columns:
            npt_data = df['npt_percentage'].dropna()
            fig.add_trace(
                go.Histogram(x=npt_data, nbinsx=20, name='NPT Distribution',
                            marker_color='red'),
                row=2, col=2
            )

        # 5. Cost Trend (if available)
        if 'cost_per_foot' in df.columns and 'spud_date' in df.columns:
            df_sorted = df.sort_values('spud_date')
            fig.add_trace(
                go.Scatter(x=df_sorted['spud_date'], y=df_sorted['cost_per_foot'],
                          mode='lines+markers', name='Cost/ft',
                          line=dict(color='purple')),
                row=3, col=1
            )

        # 6. Sidetrack Analysis
        st_analysis = self.analyzer.sidetrack_analysis()
        if not st_analysis.empty:
            st_counts = st_analysis['num_sidetracks'].value_counts().sort_index()
            fig.add_trace(
                go.Bar(x=st_counts.index, y=st_counts.values,
                       name='Wells by Sidetrack Count',
                       marker_color='teal'),
                row=3, col=2
            )

        fig.update_layout(
            height=1200,
            title_text=title,
            showlegend=True
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))

        return output_path

    def generate_well_comparison(self, api_list: List[str], output_path: Path):
        """
        Generate well-by-well comparison report.

        Args:
            api_list: List of API numbers to compare
            output_path: Path for HTML output
        """
        wells = [r for r in self.analyzer.records if r.api.api_12 in api_list]

        if not wells:
            logger.warning("No matching wells found for comparison")
            return None

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Drilling Duration',
                'Total Depth',
                'ROP Comparison',
                'Water Depth vs Duration'
            )
        )

        well_names = [w.api.api_12 for w in wells]
        durations = [w.drilling_duration or 0 for w in wells]
        depths = [w.total_depth_md_ft for w in wells]
        rops = [w.overall_rop or 0 for w in wells]
        water_depths = [w.water_depth_ft for w in wells]

        # Duration comparison
        fig.add_trace(
            go.Bar(x=well_names, y=durations, name='Duration (days)'),
            row=1, col=1
        )

        # Depth comparison
        fig.add_trace(
            go.Bar(x=well_names, y=depths, name='TD (ft)'),
            row=1, col=2
        )

        # ROP comparison
        fig.add_trace(
            go.Bar(x=well_names, y=rops, name='ROP (ft/hr)'),
            row=2, col=1
        )

        # Scatter: Water Depth vs Duration
        fig.add_trace(
            go.Scatter(x=water_depths, y=durations, mode='markers+text',
                      text=well_names, textposition='top center',
                      name='Wells'),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text="Well Comparison Analysis",
            showlegend=True
        )

        fig.write_html(str(output_path))
        return output_path
```

## YAML Configuration

### Drilling Analysis Configuration

```yaml
# config/drilling_analysis.yaml

metadata:
  task: drilling_performance_analysis
  created: "2024-01-15"

wells:
  # List of API numbers to analyze
  - api: "177104913000"
    name: "Anchor A-1"
  - api: "177104913001"
    name: "Anchor A-1 ST1"
  - api: "177590301100"
    name: "Tiber-1"

area_filter:
  codes:
    - "710"  # Green Canyon
    - "759"  # Walker Ridge

  water_depth_range:
    min_ft: 4000
    max_ft: 10000

analysis:
  benchmark_by_area: true
  benchmark_by_operator: true
  benchmark_by_water_depth: true
  sidetrack_analysis: true
  afe_estimation: true

benchmarking:
  similarity_criteria:
    max_depth_diff_ft: 2000
    max_water_depth_diff_ft: 500

output:
  benchmark_report: "reports/drilling_benchmark.html"
  comparison_report: "reports/well_comparison.html"
  afe_report: "reports/afe_estimates.csv"
  raw_data: "data/results/drilling_analysis.csv"
```

### AFE Configuration

```yaml
# config/afe_estimate.yaml

metadata:
  task: afe_estimation
  well_name: "Proposed Well A-1"

target_well:
  area: "Green Canyon"
  block: "640"
  proposed_td_ft: 25000
  water_depth_ft: 7000
  well_type: "development"

benchmark_criteria:
  area_codes:
    - "710"  # Same area preferred
    - "759"  # Similar areas
  depth_range_ft: 3000
  water_depth_range_ft: 1000
  well_types:
    - "development"
    - "exploration"

cost_parameters:
  rig_day_rate_usd: 450000
  spread_cost_multiplier: 1.4  # Include support vessels, etc.
  contingency_pct: 15

output:
  afe_summary: "reports/afe_gc640_a1.html"
  cost_breakdown: "data/results/afe_breakdown.csv"
```

## CLI Usage

### API Number Operations

```bash
# Parse and validate API number
python -m drilling_analyzer parse "177104913001"

# Find all sidetracks for a well
python -m drilling_analyzer sidetracks --api 1771049130

# List wells by area
python -m drilling_analyzer list --area GC --water-depth-min 5000
```

### Benchmarking

```bash
# Benchmark by area
python -m drilling_analyzer benchmark --by area --output reports/area_benchmark.html

# Benchmark by operator
python -m drilling_analyzer benchmark --by operator --min-wells 3

# Generate AFE estimate
python -m drilling_analyzer afe --td 25000 --water-depth 7000 --area GC
```

### Reports

```bash
# Generate comprehensive benchmark report
python -m drilling_analyzer report --config config/drilling_analysis.yaml

# Compare specific wells
python -m drilling_analyzer compare --apis 177104913000,177104913001,177590301100

# Generate efficiency metrics
python -m drilling_analyzer efficiency --output reports/efficiency.csv
```

## Usage Examples

### Example 1: Parse and Analyze API Numbers

```python
from drilling_analyzer import DrillingAnalyzer, APINumber

# Initialize analyzer
analyzer = DrillingAnalyzer()

# Parse different API formats
api_10 = analyzer.parse_api("1771049130")
api_12 = analyzer.parse_api("177104913001")
api_14 = analyzer.parse_api("17710491300102")

print(f"API-10: {api_10.api_10}")
print(f"  State: {api_10.state_code}")
print(f"  County/Area: {api_10.county_code}")
print(f"  Well: {api_10.well_sequence}")
print(f"  Area Name: {analyzer.get_area_name(api_10)}")

print(f"\nAPI-12: {api_12.api_12}")
print(f"  Is Sidetrack: {api_12.is_sidetrack}")
print(f"  Sidetrack #: {api_12.sidetrack_number}")
print(f"  Parent API: {api_12.parent_api}")
```

### Example 2: Load and Benchmark Drilling Data

```python
from drilling_analyzer import DrillingAnalyzer, DrillingRecord, APINumber, WellType
from bsee_extractor import BSEEDataClient
from datetime import date

# Initialize BSEE client
client = BSEEDataClient()

# Query WAR data for Green Canyon
activities = client.query_war_by_block("GC", "640")

# Convert to DrillingRecords
records = []
for activity in activities:
    for war in activity.war_records:
        if war.activity_type.value == 'drilling':
            record = DrillingRecord(
                api=APINumber(war.well_id.api_number),
                well_name=war.well_id.well_name,
                operator=war.operator_name,
                rig_name=war.rig_name,
                spud_date=war.spud_date,
                water_depth_ft=war.water_depth_ft or 0,
                total_depth_md_ft=war.total_depth_md or 0,
                target_formation=war.target_formation
            )
            records.append(record)

# Create analyzer
analyzer = DrillingAnalyzer(records)

# Benchmark by area
area_benchmark = analyzer.benchmark_by_area()
print("Drilling Performance by Area:")
print(area_benchmark)

# Benchmark by operator
operator_benchmark = analyzer.benchmark_by_operator()
print("\nTop Operators by Well Count:")
print(operator_benchmark.head(10))
```

### Example 3: AFE Estimation

```python
# Create target well for AFE
target = DrillingRecord(
    api=APINumber("17710496400"),  # Proposed well in GC
    well_name="Proposed GC640 A-1",
    well_type=WellType.DEVELOPMENT,
    water_depth_ft=7000,
    total_depth_md_ft=25000,
    daily_rig_rate_usd=450000
)

# Get AFE estimate
afe_estimate = analyzer.calculate_afe_estimate(target)

print("AFE Estimate for", target.well_name)
print(f"  Based on {afe_estimate['similar_wells_count']} similar wells")
print(f"\n  Duration Estimate (days):")
print(f"    P10: {afe_estimate['duration_estimate_days']['p10']:.0f}")
print(f"    P50: {afe_estimate['duration_estimate_days']['p50']:.0f}")
print(f"    P90: {afe_estimate['duration_estimate_days']['p90']:.0f}")

if 'cost_estimate_usd' in afe_estimate:
    print(f"\n  Cost Estimate (USD):")
    print(f"    P10: ${afe_estimate['cost_estimate_usd']['p10']:,.0f}")
    print(f"    P50: ${afe_estimate['cost_estimate_usd']['p50']:,.0f}")
    print(f"    P90: ${afe_estimate['cost_estimate_usd']['p90']:,.0f}")
```

### Example 4: Sidetrack Analysis

```python
# Analyze sidetracks
sidetrack_df = analyzer.sidetrack_analysis()

print("Sidetrack Analysis:")
print(f"  Wells with no sidetracks: {len(sidetrack_df[sidetrack_df['num_sidetracks'] == 0])}")
print(f"  Wells with 1+ sidetracks: {len(sidetrack_df[sidetrack_df['num_sidetracks'] > 0])}")

# Find specific well's sidetracks
parent_api = "1771049130"
sidetracks = analyzer.find_sidetracks(parent_api)
print(f"\nSidetracks for {parent_api}:")
for st in sidetracks:
    print(f"  {st.api.api_12}: TD={st.total_depth_md_ft:,.0f}ft, Duration={st.drilling_duration} days")
```

### Example 5: Generate Reports

```python
from drilling_analyzer import DrillingReportGenerator
from pathlib import Path

# Create report generator
reporter = DrillingReportGenerator(analyzer)

# Generate benchmark report
reporter.generate_benchmark_report(
    output_path=Path("reports/gc_drilling_benchmark.html"),
    title="Green Canyon Drilling Benchmark"
)

# Compare specific wells
wells_to_compare = ["177104913000", "177104913001", "177590301100"]
reporter.generate_well_comparison(
    api_list=wells_to_compare,
    output_path=Path("reports/well_comparison.html")
)

print("Reports generated successfully!")
```

## Best Practices

### API Number Handling
- Always validate API numbers before processing
- Store API numbers as strings to preserve leading zeros
- Use the appropriate format (10, 12, or 14 digit) for your use case
- Group sidetracks with parent wells for proper analysis

### Benchmarking
- Use similar wells (water depth, TD, well type) for accurate comparisons
- Account for learning curve effects when comparing sequential wells
- Consider rig capabilities when benchmarking ROP
- Include NPT analysis to identify improvement opportunities

### AFE Estimation
- Use P50 for planning, P90 for contingency
- Include at least 5-10 analog wells for reliable estimates
- Adjust for rig type and technology differences
- Update estimates as drilling progresses

### File Organization
```
project/
├── config/
│   ├── drilling_analysis.yaml
│   └── afe_estimate.yaml
├── data/
│   ├── bsee_cache/
│   └── results/
│       ├── drilling_analysis.csv
│       └── afe_breakdown.csv
├── reports/
│   ├── drilling_benchmark.html
│   └── well_comparison.html
└── src/
    └── drilling_analyzer/
        ├── api_parser.py
        ├── analyzer.py
        ├── benchmarking.py
        └── reports.py
```

## Related Skills

- [bsee-data-extractor](../bsee-data-extractor/SKILL.md) - Source data for drilling analysis
- [npv-analyzer](../npv-analyzer/SKILL.md) - Economic analysis using drilling costs
- [production-forecaster](../production-forecaster/SKILL.md) - Link drilling to production outcomes
- [hse-risk-analyzer](../hse-risk-analyzer/SKILL.md) - Safety metrics for drilling operations
