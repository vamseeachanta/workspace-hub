---
name: bsee-data-extractor-example-1-single-well-analysis
description: 'Sub-skill of bsee-data-extractor: Example 1: Single Well Analysis (+5).'
version: 1.0.0
category: data/energy
type: reference
scripts_exempt: true
---

# Example 1: Single Well Analysis (+5)

## Example 1: Single Well Analysis


```python
from bsee_extractor import BSEEDataClient, BSEEReportGenerator

# Initialize client
client = BSEEDataClient(cache_dir=Path("data/bsee_cache"))

# Query well production
well = client.query_by_api("1771049130", start_year=2010, end_year=2024)

# Get production DataFrame
df = well.to_dataframe()
print(f"Records: {len(df)}")
print(f"Cumulative Oil: {well.cumulative_oil:,.0f} bbls")
print(f"Cumulative Gas: {well.cumulative_gas:,.0f} MCF")

# Generate report
from production_aggregator import ProductionAggregator
aggregator = ProductionAggregator([well])
reporter = BSEEReportGenerator(aggregator)
reporter.generate_well_report(well, Path("reports/well_analysis.html"))
```


## Example 2: Block-Level Analysis


```python
# Query all wells in Green Canyon Block 640
wells = client.query_by_block("GC", "640", year=2023)
print(f"Found {len(wells)} wells in GC 640")

# Aggregate production
aggregator = ProductionAggregator(wells)

# Monthly totals
monthly = aggregator.monthly_totals()
print(f"\n2023 Production:")
print(f"  Total Oil: {monthly['oil_bbls'].sum():,.0f} bbls")
print(f"  Total Gas: {monthly['gas_mcf'].sum():,.0f} MCF")

# Well summary
summary = aggregator.well_summary()
print(f"\nWell Rankings by Cumulative Oil:")
print(summary.sort_values('cumulative_oil', ascending=False)[
    ['api_number', 'cumulative_oil', 'peak_oil_bopd']
].head(10))

# Generate field report
reporter = BSEEReportGenerator(aggregator)
reporter.generate_field_report(
    Path("reports/gc640_production.html"),
    field_name="Green Canyon 640"
)
```


## Example 3: Decline Curve Preparation


```python
# Get decline curve data for type curve analysis
well = client.query_by_api("1771049130")
decline_data = aggregator.decline_curve_data(well)

# Prepare for Arps decline fitting
import numpy as np

time = np.array(decline_data['time'])
rate = np.array(decline_data['rate'])

# Filter to producing periods only
mask = rate > 0
time_producing = time[mask]
rate_producing = rate[mask]

# Export for external decline curve software
decline_df = pd.DataFrame({
    'months': time_producing,
    'oil_bopd': rate_producing
})
decline_df.to_csv("data/decline_input.csv", index=False)
```


## Example 4: WAR Activity Analysis


```python
from bsee_extractor import BSEEDataClient, ActivityAggregator

# Initialize client
client = BSEEDataClient(cache_dir=Path("data/bsee_cache"))

# Query WAR data for a specific well
well_activity = client.query_war_by_api("1771049130")

# Get WAR DataFrame
war_df = well_activity.to_war_dataframe()
print(f"Total activities: {len(war_df)}")
print(f"Activity types: {war_df['activity_type'].unique()}")

# Calculate drilling and completion durations
print(f"\nTotal drilling days: {well_activity.total_drilling_days}")
print(f"Total completion days: {well_activity.total_completion_days}")

# Detailed drilling history
drilling_df = war_df[war_df['activity_type'] == 'drilling']
print(f"\nDrilling Operations:")
print(drilling_df[['start_date', 'end_date', 'duration_days', 'rig_name', 'total_depth_md']])
```


## Example 5: Block-Level Drilling Analysis


```python
# Query all well activities in Walker Ridge Block 758
activities = client.query_war_by_block("WR", "758")
print(f"Found {len(activities)} wells with WAR records in WR 758")

# Aggregate activities
activity_agg = ActivityAggregator(activities)

# Drilling timeline for rig scheduling
drilling_timeline = activity_agg.drilling_timeline()
print("\nDrilling Timeline:")
print(drilling_timeline[['api_number', 'start_date', 'rig_name', 'duration_days']])

# Rig utilization analysis
rig_util = activity_agg.rig_utilization()
print("\nRig Utilization:")
print(rig_util)

# Operator activity summary
operator_summary = activity_agg.operator_activity()
print("\nOperator Activity:")
print(operator_summary)

# Depth statistics
depth_stats = activity_agg.depth_statistics()
print(f"\nWater Depth Range: {depth_stats['water_depth']['min']:.0f} - {depth_stats['water_depth']['max']:.0f} ft")
print(f"Avg Total Depth: {depth_stats['total_depth_md']['mean']:.0f} ft MD")
```


## Example 6: APD Tracking and Permit Analysis


```python
# Query APD records for a well
apd_records = client.query_apd_by_api("1771049130")
print(f"Found {len(apd_records)} APD records")

for apd in apd_records:
    print(f"\nPermit: {apd.permit_number}")
    print(f"  Application Date: {apd.application_date}")
    print(f"  Status: {apd.status.value}")
    print(f"  Well Type: {apd.well_type}")
    if apd.approval_date:
        print(f"  Approval Date: {apd.approval_date}")
        days_to_approve = (apd.approval_date - apd.application_date).days
        print(f"  Days to Approval: {days_to_approve}")
```
