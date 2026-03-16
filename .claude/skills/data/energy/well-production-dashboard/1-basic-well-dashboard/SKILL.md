---
name: well-production-dashboard-1-basic-well-dashboard
description: 'Sub-skill of well-production-dashboard: 1. Basic Well Dashboard (+3).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# 1. Basic Well Dashboard (+3)

## 1. Basic Well Dashboard


Create interactive dashboard for well analysis.

```yaml
well_production_dashboard:
  basic:
    flag: true
    title: "Well Production Dashboard"
    wells:
      - "API_12345"
      - "API_67890"

*See sub-skills for full details.*

## 2. Field Aggregation Dashboard


Aggregate wells to field level with statistics.

```yaml
well_production_dashboard:
  field_aggregation:
    flag: true
    field_name: "ANCHOR"
    aggregation:
      - total_production
      - mean_production

*See sub-skills for full details.*

## 3. Real-Time Monitoring Dashboard


Enable real-time updates with WebSocket.

```yaml
well_production_dashboard:
  real_time:
    flag: true
    enable_real_time: true
    update_interval_ms: 60000
    websocket_port: 8765
    api_port: 5000

*See sub-skills for full details.*

## 4. Economic Analysis Dashboard


Dashboard with financial metrics.

```yaml
well_production_dashboard:
  economics:
    flag: true
    wells:
      - "API_12345"
    metrics:
      - npv

*See sub-skills for full details.*
