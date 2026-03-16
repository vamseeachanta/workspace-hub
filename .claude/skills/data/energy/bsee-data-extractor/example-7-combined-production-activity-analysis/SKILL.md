---
name: bsee-data-extractor-example-7-combined-production-activity-analysis
description: 'Sub-skill of bsee-data-extractor: Example 7: Combined Production + Activity
  Analysis.'
version: 1.0.0
category: data/energy
type: reference
scripts_exempt: true
---

# Example 7: Combined Production + Activity Analysis

## Example 7: Combined Production + Activity Analysis


```python
# Get both production and activity data for a well
well_production = client.query_by_api("1771049130", start_year=2015)
well_activity = client.query_war_by_api("1771049130")

# Combine for comprehensive well analysis
print(f"Well: {well_production.well_id.api_number}")
print(f"\n--- Production Summary ---")
print(f"First Production: {well_production.first_production}")
print(f"Cumulative Oil: {well_production.cumulative_oil:,.0f} bbls")
print(f"Cumulative Gas: {well_production.cumulative_gas:,.0f} MCF")

print(f"\n--- Activity Summary ---")
print(f"First Activity: {well_activity.first_activity}")
print(f"Drilling Days: {well_activity.total_drilling_days}")
print(f"Completion Days: {well_activity.total_completion_days}")
print(f"Total WAR Records: {len(well_activity.war_records)}")

# Calculate time from spud to first production
war_df = well_activity.to_war_dataframe()
drilling_records = war_df[war_df['activity_type'] == 'drilling']
if not drilling_records.empty and well_production.first_production:
    spud_date = drilling_records['spud_date'].min()
    if spud_date:
        days_to_production = (well_production.first_production - spud_date).days
        print(f"\nDays from Spud to First Production: {days_to_production}")
```
