---
name: autoviz-2-chart-format-and-output-options
description: 'Sub-skill of autoviz: 2. Chart Format and Output Options (+1).'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 2. Chart Format and Output Options (+1)

## 2. Chart Format and Output Options


**Different Chart Formats:**
```python
from autoviz import AutoViz_Class
import pandas as pd

df = pd.read_csv("data.csv")
AV = AutoViz_Class()

# SVG format (vector, scalable)
df_svg = AV.AutoViz(
    filename="",
    dfte=df,
    chart_format="svg",  # Scalable vector graphics
    verbose=1
)

# PNG format (raster, good for presentations)
df_png = AV.AutoViz(
    filename="",
    dfte=df,
    chart_format="png",  # PNG images
    verbose=1
)

# HTML format (interactive, for web)
df_html = AV.AutoViz(
    filename="",
    dfte=df,
    chart_format="html",  # Interactive HTML
    verbose=1
)

# Bokeh backend for interactive plots
df_bokeh = AV.AutoViz(
    filename="",
    dfte=df,
    chart_format="bokeh",  # Bokeh interactive
    verbose=1
)

# Server mode (for Jupyter notebooks)
df_server = AV.AutoViz(
    filename="",
    dfte=df,
    chart_format="server",  # Inline in notebook
    verbose=1
)
```

**Saving Charts to Directory:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import os

# Create output directory
output_dir = "analysis_output"
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv("data.csv")
AV = AutoViz_Class()

# Save all charts to specified directory
df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    chart_format="png",
    save_plot_dir=output_dir,  # Directory to save plots
    verbose=1
)

# List generated files
for file in os.listdir(output_dir):
    print(f"Generated: {file}")
```


## 3. Handling Large Datasets


**Sampling Strategies:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import numpy as np

# Create large dataset
np.random.seed(42)
large_df = pd.DataFrame({
    "feature_" + str(i): np.random.randn(500000)
    for i in range(20)
})
large_df["category"] = np.random.choice(["A", "B", "C", "D"], 500000)
large_df["target"] = np.random.randint(0, 2, 500000)

print(f"Dataset size: {large_df.shape}")

AV = AutoViz_Class()

# Control sampling with max_rows_analyzed
df_analyzed = AV.AutoViz(
    filename="",
    dfte=large_df,
    max_rows_analyzed=100000,  # Sample 100K rows
    max_cols_analyzed=25,  # Limit columns analyzed
    verbose=1,
    chart_format="png"
)

# For very large datasets, use smaller sample
df_analyzed_small = AV.AutoViz(
    filename="",
    dfte=large_df,
    max_rows_analyzed=50000,  # Smaller sample for speed
    max_cols_analyzed=15,
    verbose=0,  # Minimal output
    chart_format="svg"
)
```

**Memory-Efficient Analysis:**
```python
from autoviz import AutoViz_Class
import pandas as pd

def analyze_large_file(file_path: str, sample_size: int = 100000) -> pd.DataFrame:
    """
    Analyze large files efficiently with sampling.

    Args:
        file_path: Path to CSV file
        sample_size: Number of rows to sample

    Returns:
        Analyzed DataFrame
    """
    # Read only a sample for initial analysis
    total_rows = sum(1 for _ in open(file_path)) - 1  # Exclude header

    if total_rows > sample_size:
        # Calculate skip probability
        skip_prob = 1 - (sample_size / total_rows)

        # Read with sampling
        df = pd.read_csv(
            file_path,
            skiprows=lambda i: i > 0 and np.random.random() < skip_prob
        )
    else:
        df = pd.read_csv(file_path)

    print(f"Sampled {len(df)} rows from {total_rows} total")

    AV = AutoViz_Class()
    return AV.AutoViz(
        filename="",
        dfte=df,
        verbose=1,
        chart_format="png"
    )

# Usage
# df_result = analyze_large_file("huge_dataset.csv", sample_size=75000)
```
