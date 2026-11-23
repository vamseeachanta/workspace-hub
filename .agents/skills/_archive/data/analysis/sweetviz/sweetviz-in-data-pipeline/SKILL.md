---
name: sweetviz-sweetviz-in-data-pipeline
description: 'Sub-skill of sweetviz: Sweetviz in Data Pipeline.'
version: 1.0.0
category: data-analysis
type: reference
scripts_exempt: true
---

# Sweetviz in Data Pipeline

## Sweetviz in Data Pipeline


```python
#!/usr/bin/env python3
"""data_pipeline_sweetviz.py - Integrate Sweetviz in data pipeline"""

import sweetviz as sv
import pandas as pd
import numpy as np
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPipelineProfiler:
    """Sweetviz profiler for data pipelines."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.reports = []

    def profile_stage(
        self,
        df: pd.DataFrame,
        stage_name: str,
        target_col: str = None,
        previous_df: pd.DataFrame = None
    ) -> str:
        """
        Profile data at a pipeline stage.

        Args:
            df: DataFrame at current stage
            stage_name: Name of the pipeline stage
            target_col: Target variable (optional)
            previous_df: DataFrame from previous stage (optional)

        Returns:
            Path to generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if previous_df is not None:
            # Comparison report
            logger.info(f"Generating comparison report for stage: {stage_name}")

            report = sv.compare(
                source=[previous_df, "Before"],
                compare=[df, "After"],
                target_feat=target_col
            )

            report_path = os.path.join(
                self.output_dir,
                f"{stage_name}_comparison_{timestamp}.html"
            )
        else:
            # Single analysis report
            logger.info(f"Generating analysis report for stage: {stage_name}")

            report = sv.analyze(
                source=df,
                target_feat=target_col
            )

            report_path = os.path.join(
                self.output_dir,
                f"{stage_name}_analysis_{timestamp}.html"
            )

        report.show_html(report_path, open_browser=False)
        self.reports.append(report_path)

        logger.info(f"Report saved: {report_path}")
        return report_path

    def generate_summary(self) -> dict:
        """Generate summary of all profiling reports."""
        return {
            "total_reports": len(self.reports),
            "reports": self.reports,
            "output_dir": self.output_dir
        }


# Example pipeline usage
def example_pipeline():
    """Example data pipeline with profiling."""
    profiler = DataPipelineProfiler("pipeline_reports")

    # Stage 1: Raw data
    np.random.seed(42)
    df_raw = pd.DataFrame({
        "value": np.concatenate([np.random.randn(950), [100, -50, np.nan] * 10]),
        "category": np.random.choice(["A", "B", "C"], 980),
        "target": np.random.choice([0, 1], 980)
    })

    profiler.profile_stage(df_raw, "01_raw_data", target_col="target")

    # Stage 2: Missing value handling
    df_cleaned = df_raw.copy()
    df_cleaned["value"] = df_cleaned["value"].fillna(df_cleaned["value"].median())

    profiler.profile_stage(
        df_cleaned, "02_missing_handled",
        target_col="target",
        previous_df=df_raw
    )

    # Stage 3: Outlier removal
    Q1 = df_cleaned["value"].quantile(0.25)
    Q3 = df_cleaned["value"].quantile(0.75)
    IQR = Q3 - Q1

    df_no_outliers = df_cleaned[
        (df_cleaned["value"] >= Q1 - 1.5 * IQR) &
        (df_cleaned["value"] <= Q3 + 1.5 * IQR)
    ]

    profiler.profile_stage(
        df_no_outliers, "03_outliers_removed",
        target_col="target",
        previous_df=df_cleaned
    )

    # Summary
    summary = profiler.generate_summary()
    print(f"\nPipeline profiling complete!")
    print(f"Generated {summary['total_reports']} reports")

    return summary


if __name__ == "__main__":
    example_pipeline()
```
