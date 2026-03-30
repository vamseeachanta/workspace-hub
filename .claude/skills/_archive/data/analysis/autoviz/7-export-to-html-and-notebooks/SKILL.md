---
name: autoviz-7-export-to-html-and-notebooks
description: 'Sub-skill of autoviz: 7. Export to HTML and Notebooks.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# 7. Export to HTML and Notebooks

## 7. Export to HTML and Notebooks


**HTML Report Generation:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import os

def generate_html_report(
    df: pd.DataFrame,
    output_dir: str,
    report_name: str = "eda_report",
    target: str = ""
) -> str:
    """
    Generate comprehensive HTML report with AutoViz.

    Args:
        df: Input DataFrame
        output_dir: Directory for output files
        report_name: Name for the report
        target: Target variable (optional)

    Returns:
        Path to generated report
    """
    os.makedirs(output_dir, exist_ok=True)

    AV = AutoViz_Class()

    # Generate HTML charts
    df_analyzed = AV.AutoViz(
        filename="",
        dfte=df,
        depVar=target,
        chart_format="html",
        save_plot_dir=output_dir,
        verbose=1
    )

    # Create summary HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{report_name} - AutoViz EDA Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
            .chart-container {{ margin: 20px 0; }}
        </style>
    </head>
    <body>
        <h1>{report_name}</h1>

        <div class="summary">
            <h2>Dataset Summary</h2>
            <p>Rows: {len(df):,}</p>
            <p>Columns: {len(df.columns)}</p>
            <p>Numeric columns: {len(df.select_dtypes(include=['number']).columns)}</p>
            <p>Categorical columns: {len(df.select_dtypes(include=['object', 'category']).columns)}</p>
            <p>Target variable: {target if target else 'Not specified'}</p>
        </div>

        <h2>Column Information</h2>
        <table border="1" style="border-collapse: collapse;">
            <tr><th>Column</th><th>Type</th><th>Non-Null</th><th>Unique</th></tr>
    """

    for col in df.columns:
        html_content += f"""
            <tr>
                <td>{col}</td>
                <td>{df[col].dtype}</td>
                <td>{df[col].notna().sum()}</td>
                <td>{df[col].nunique()}</td>
            </tr>
        """

    html_content += """
        </table>

        <h2>Generated Charts</h2>
        <p>Charts have been saved to the output directory.</p>
    </body>
    </html>
    """

    report_path = os.path.join(output_dir, f"{report_name}.html")
    with open(report_path, "w") as f:
        f.write(html_content)

    return report_path

# Usage
# report_path = generate_html_report(df, "output/eda", "sales_analysis", "revenue")
# print(f"Report saved to: {report_path}")
```

**Jupyter Notebook Integration:**
```python
# In Jupyter Notebook
from autoviz import AutoViz_Class
import pandas as pd

# Load data
df = pd.read_csv("data.csv")

# Initialize AutoViz
AV = AutoViz_Class()

# Use 'server' format for inline display in notebooks
%matplotlib inline

df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    depVar="target",
    chart_format="server",  # Display inline in notebook
    verbose=1
)

# Alternative: Use bokeh for interactive plots in notebooks
df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    depVar="target",
    chart_format="bokeh",  # Interactive Bokeh plots
    verbose=1
)
```

**Export to Notebook File:**
```python
from autoviz import AutoViz_Class
import pandas as pd
import nbformat as nbf
import os

def create_eda_notebook(
    df: pd.DataFrame,
    output_path: str,
    dataset_name: str = "dataset"
) -> str:
    """
    Create a Jupyter notebook with AutoViz EDA.

    Args:
        df: Input DataFrame
        output_path: Path for output notebook
        dataset_name: Name for the dataset

    Returns:
        Path to created notebook
    """
    nb = nbf.v4.new_notebook()

    cells = [
        nbf.v4.new_markdown_cell(f"# Exploratory Data Analysis: {dataset_name}"),

        nbf.v4.new_code_cell("""
from autoviz import AutoViz_Class
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
"""),

        nbf.v4.new_markdown_cell("## Load Data"),

        nbf.v4.new_code_cell(f"""
# Data is pre-loaded
df = pd.read_csv("{dataset_name}.csv")  # Update path as needed
print(f"Dataset shape: {{df.shape}}")
df.head()
"""),

        nbf.v4.new_markdown_cell("## AutoViz Analysis"),

        nbf.v4.new_code_cell("""
AV = AutoViz_Class()

df_analyzed = AV.AutoViz(
    filename="",
    dfte=df,
    chart_format="server",

*Content truncated — see parent skill for full reference.*
