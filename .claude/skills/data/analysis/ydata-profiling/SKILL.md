---
name: ydata-profiling
version: 1.0.0
description: Automated data quality reports with comprehensive variable analysis,
  missing value detection, correlations, and HTML report generation - formerly pandas-profiling
type: reference
author: workspace-hub
category: data-analysis
capabilities:
- Automated data quality reports
- Variable type inference and analysis
- Missing value detection and patterns
- Correlation analysis (Pearson, Spearman, Kendall, Phik)
- Duplicate row detection
- HTML report generation
- Large dataset handling with minimal mode
- Comparison reports between datasets
- Time series analysis
tools:
- ydata-profiling
- pandas
- numpy
- scipy
- matplotlib
tags:
- ydata-profiling
- pandas-profiling
- data-quality
- eda
- profiling
- missing-values
- correlations
- html-report
- data-analysis
platforms:
- python
related_skills:
- autoviz
- pandas-data-processing
- polars
- great-tables
- streamlit
requires: []
scripts_exempt: true
---

# Ydata Profiling

## When to Use This Skill

### USE YData Profiling when:

- **Data quality assessment** - Evaluating dataset health and completeness
- **Initial data exploration** - Understanding a new dataset quickly
- **Missing value analysis** - Detecting patterns in missing data
- **Variable analysis** - Understanding distributions and characteristics
- **Data documentation** - Creating shareable data quality reports
- **Dataset comparison** - Comparing training vs test data, or before/after
- **Stakeholder reporting** - Generating professional HTML reports
- **Data validation** - Checking data before ML model training
### DON'T USE YData Profiling when:

- **Real-time analysis** - Need streaming data profiling
- **Custom visualizations** - Specific chart requirements
- **Interactive dashboards** - Use Streamlit or Dash instead
- **Very large datasets** - Over 10M rows (use sampling or minimal mode)
- **Production pipelines** - Need lightweight validation (use Great Expectations)

## Prerequisites

```bash
# Basic installation
pip install ydata-profiling

# With all optional dependencies
pip install 'ydata-profiling[all]'

# Using uv (recommended)
uv pip install ydata-profiling pandas numpy

# Jupyter notebook support
pip install ydata-profiling ipywidgets notebook

# Verify installation
python -c "from ydata_profiling import ProfileReport; print('YData Profiling ready!')"
```

## Complete Examples

### Example 1: Data Quality Pipeline

```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json

def data_quality_pipeline(
    df: pd.DataFrame,

*See sub-skills for full details.*
### Example 2: ML Dataset Profiling

```python
from ydata_profiling import ProfileReport, compare
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

def ml_dataset_profiling(
    X: pd.DataFrame,
    y: pd.Series,

*See sub-skills for full details.*
### Example 3: Time Series Data Profiling

```python
from ydata_profiling import ProfileReport
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def profile_time_series(
    df: pd.DataFrame,
    date_column: str,

*See sub-skills for full details.*

## Version History

- **1.0.0** (2026-01-17): Initial release
  - Basic profile report generation
  - Variable analysis and type detection
  - Missing value analysis patterns
  - Correlation methods (Pearson, Spearman, Kendall, Phi-K)
  - Large dataset handling (minimal mode, sampling)
  - Comparison reports for datasets
  - HTML report customization
  - Time series profiling
  - Complete pipeline examples
  - Integration with Streamlit and Polars
  - Best practices and troubleshooting

## Resources

- **Official Documentation**: https://docs.profiling.ydata.ai/
- **GitHub**: https://github.com/ydataai/ydata-profiling
- **PyPI**: https://pypi.org/project/ydata-profiling/
- **Migration from pandas-profiling**: https://docs.profiling.ydata.ai/latest/migration/

---

**Generate comprehensive data quality reports automatically with YData Profiling!**

## Sub-Skills

- [1. Basic Profile Report Generation (+1)](1-basic-profile-report-generation/SKILL.md)
- [3. Missing Value Analysis (+1)](3-missing-value-analysis/SKILL.md)
- [5. Large Dataset Handling](5-large-dataset-handling/SKILL.md)
- [6. Comparison Reports](6-comparison-reports/SKILL.md)
- [7. HTML Report Customization](7-html-report-customization/SKILL.md)
- [YData Profiling with Streamlit (+1)](ydata-profiling-with-streamlit/SKILL.md)
- [1. Use Minimal Mode for Large Datasets (+3)](1-use-minimal-mode-for-large-datasets/SKILL.md)
- [Common Issues](common-issues/SKILL.md)
