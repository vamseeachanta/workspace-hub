---
name: forecast
type: command
plugin: sales
source: https://github.com/anthropics/knowledge-work-plugins
---

# Sales Forecast Tool Overview

The `/forecast` command generates weighted sales projections with risk analysis and actionable recommendations.

## Key Features

**Core Capabilities:**
The tool produces risk-adjusted projections (best/likely/worst case) alongside commit versus upside breakdowns and gap analysis to quota.

**Data Input Options:**
Users can provide pipeline information via CSV export, manual deal descriptions, or territory summaries. Minimum required fields include deal name, amount, stage, and close date.

**Analysis Output:**
The forecast delivers scenario modeling across three conditions, stage-based probability weighting, deal-level risk flagging, and specific recommendations to close quota gaps.

**Probability Framework:**
Default stage probabilities range from 10% (prospecting) to 100% (closed won), adjustable based on your actual historical win rates.

**Standalone vs. Connected:**
The tool works independently with uploaded data, but gains real-time pipeline pulls, historical win-rate analytics, and activity-based risk scoring when CRM integrations are active.

## Practical Value

The structured output distinguishes between high-confidence deals worth committing to and lower-confidence opportunities, helping sales leaders set realistic forecasts while identifying acceleration levers for quota attainment.
