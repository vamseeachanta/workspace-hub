---
name: data-analysis-data-pipeline-architecture
description: 'Sub-skill of data-analysis: Data Pipeline Architecture (+2).'
version: 1.0.0
category: data
type: reference
scripts_exempt: true
---

# Data Pipeline Architecture (+2)

## Data Pipeline Architecture


```
Raw Data --> Ingestion --> Processing --> Analysis --> Visualization --> Reporting
    |            |             |             |              |              |
    +-- Files   +-- Validate  +-- polars   +-- EDA tools  +-- streamlit  +-- great-tables
    +-- APIs    +-- Clean     +-- Transform +-- Profiling  +-- dash       +-- Export
    +-- DB      +-- Schema    +-- Aggregate +-- Insights   +-- Charts     +-- Share
```

## Dashboard Development Flow


```
Requirements --> Prototype --> Iterate --> Deploy --> Monitor
      |              |            |           |           |
      +-- Metrics   +-- streamlit +-- Feedback +-- Cloud  +-- Usage
      +-- Users     +-- Mock data +-- Polish   +-- Auth   +-- Performance
      +-- Frequency +-- Layout    +-- Test     +-- Scale  +-- Alerts
```

## EDA Workflow


```
Load Data --> Profile --> Visualize --> Document --> Share
     |            |            |            |           |
     +-- Sample  +-- ydata    +-- autoviz  +-- Findings +-- HTML
     +-- Schema  +-- sweetviz +-- Custom   +-- Issues   +-- Notebook
     +-- Types   +-- Alerts   +-- Explore  +-- Next     +-- Slides
```
