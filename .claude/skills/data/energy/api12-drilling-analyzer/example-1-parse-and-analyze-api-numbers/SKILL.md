---
name: api12-drilling-analyzer-example-1-parse-and-analyze-api-numbers
description: 'Sub-skill of api12-drilling-analyzer: Example 1: Parse and Analyze API
  Numbers (+4).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Example 1: Parse and Analyze API Numbers (+4)

## Example 1: Parse and Analyze API Numbers


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


## Example 2: Load and Benchmark Drilling Data


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


## Example 3: AFE Estimation


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


## Example 4: Sidetrack Analysis


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


## Example 5: Generate Reports


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
