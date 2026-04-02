---
name: streamlit
version: 1.0.0
description: Build interactive data applications and dashboards with pure Python -
  no frontend experience required
type: reference
author: workspace-hub
category: data-analysis
capabilities:
- Rapid prototyping of data applications
- Interactive widgets and user inputs
- Data visualization integration (Plotly, Matplotlib, Altair)
- Caching for performance optimization
- Session state management
- Multi-page application support
- Cloud deployment ready
tools:
- streamlit
- plotly
- pandas
- polars
tags:
- streamlit
- dashboard
- data-app
- visualization
- python
- web-app
- interactive
- prototyping
platforms:
- python
- web
related_skills:
- polars
- dash
- plotly
- pandas-data-processing
requires: []
scripts_exempt: true
---

# Streamlit

## When to Use This Skill

### USE Streamlit when:

- **Rapid prototyping** - Need to build a data app quickly
- **Internal tools** - Creating tools for your team
- **Data exploration** - Interactive exploration of datasets
- **Demo applications** - Showcasing data science projects
- **ML model demos** - Building interfaces for model inference
- **Simple dashboards** - Quick insights without complex setup
- **Python-only development** - No JavaScript/frontend knowledge required
### DON'T USE Streamlit when:

- **Complex interactivity** - Need fine-grained callback control (use Dash)
- **Enterprise deployment** - Require advanced authentication/scaling (use Dash Enterprise)
- **Custom components** - Heavy custom JavaScript requirements
- **High-traffic production** - Thousands of concurrent users
- **Real-time streaming** - Sub-second update requirements

## Prerequisites

```bash
# Basic installation
pip install streamlit

# With common extras
pip install streamlit plotly pandas polars

# Using uv (recommended)
uv pip install streamlit plotly pandas polars altair

# Verify installation
streamlit hello
```

## Complete Examples

### Example 1: Sales Dashboard

```python
import streamlit as st
import pandas as pd
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(

*See sub-skills for full details.*
### Example 2: Data Explorer Tool

```python
import streamlit as st
import pandas as pd
import polars as pl
import plotly.express as px

st.set_page_config(page_title="Data Explorer", page_icon="🔍", layout="wide")

st.title("🔍 Interactive Data Explorer")


*See sub-skills for full details.*
### Example 3: ML Model Demo

```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

st.set_page_config(page_title="ML Demo", page_icon="🤖", layout="wide")

*See sub-skills for full details.*

## Deployment Patterns

### Streamlit Cloud Deployment

```yaml
# requirements.txt
streamlit>=1.32.0
pandas>=2.0.0
polars>=0.20.0
plotly>=5.18.0
numpy>=1.24.0
```

```toml

*See sub-skills for full details.*
### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

*See sub-skills for full details.*

## Version History

- **1.0.0** (2026-01-17): Initial release
  - Basic app structure and widgets
  - Layout and organization patterns
  - Data visualization integration
  - Caching strategies
  - Session state management
  - Multi-page applications
  - Complete dashboard examples
  - Deployment patterns
  - Best practices and troubleshooting

## Resources

- **Official Docs**: https://docs.streamlit.io/
- **Gallery**: https://streamlit.io/gallery
- **Components**: https://streamlit.io/components
- **Cloud**: https://streamlit.io/cloud
- **GitHub**: https://github.com/streamlit/streamlit

---

**Build beautiful data apps with pure Python - no frontend experience required!**

## Sub-Skills

- [1. Basic Application Structure (+1)](1-basic-application-structure/SKILL.md)
- [3. Layout and Organization](3-layout-and-organization/SKILL.md)
- [4. Data Visualization (+1)](4-data-visualization/SKILL.md)
- [6. Session State (+1)](6-session-state/SKILL.md)
- [8. Advanced Features](8-advanced-features/SKILL.md)
- [1. Use Caching Appropriately (+3)](1-use-caching-appropriately/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
