---
name: crossprovider gemini analysis-pipelines-extract-analyze-report-with-o
description: Analysis pipelines: Extract → Analyze → Report with optional phases
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pipeline-design, analysis-workflow]
---

Structure field/fleet analysis as Extract (load data) → Analyze (compute summaries) → Report (render output), with optional long-running phases (decline curves, benchmarks) that gracefully skip if insufficient data. Provide multiple output formats (HTML report + CSV exports) in a single run.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
