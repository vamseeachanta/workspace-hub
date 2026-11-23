---
name: pipeline-review
type: command
plugin: sales
source: https://github.com/anthropics/knowledge-work-plugins
---

# Pipeline Review Command Summary

The `/pipeline-review` command analyzes sales pipeline health and delivers actionable priorities. Here's what it does:

## Core Functionality

This tool evaluates your deals across multiple dimensions using a **health score** covering stage progression, activity recency, close date accuracy, and contact coverage. It then ranks opportunities by impact and closability.

## Input Options

You can provide data three ways:
- Upload a CRM export (CSV format)
- Paste individual deal details
- Describe your pipeline verbally

## Key Outputs

The analysis generates:
- Overall pipeline health rating (0-100 scale)
- Prioritized action list for the week
- Risk identification (stale deals, stuck opportunities, overdue closes, single-threaded relationships)
- Pipeline distribution by stage, month, and deal size
- Specific hygiene recommendations

## Prioritization Approach

The command weights factors as: close timing (30%), deal magnitude (25%), stage advancement (20%), engagement level (15%), and risk profile (10%). You can adjust these weights based on your strategy.

## Value Proposition

This delivers actionable recommendations for where to focus, enabling reps and leaders to concentrate efforts on deals most likely to close while surfacing problems before they become pipeline failures.
