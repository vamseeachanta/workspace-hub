---
name: economic-sensitivity-analyzer
version: 1.0.0
category: data
description: Perform advanced economic sensitivity analysis for oil & gas investments
  including spider diagrams, 2D surfaces, breakeven analysis, and decision tree analysis.
command: /economic-sensitivity-analyzer
author: worldenergydata
tags:
- economics
- sensitivity
- analysis
- visualization
- decision-support
see_also:
- economic-sensitivity-analyzer-sensitivityparameter
- economic-sensitivity-analyzer-yaml-configuration
- economic-sensitivity-analyzer-cli-usage
- economic-sensitivity-analyzer-example-complete-sensitivity-analysis
- economic-sensitivity-analyzer-output-formats
---

# Economic Sensitivity Analyzer

## Overview

The Economic Sensitivity Analyzer provides advanced visualization and analysis tools for understanding how economic parameters affect project NPV. While the npv-analyzer provides basic sensitivity analysis, this skill focuses on multi-dimensional sensitivity visualization, breakeven analysis, and decision support tools.

## When to Use

Use this skill when you need to:
- Create spider diagrams showing multi-parameter sensitivity
- Generate 2D sensitivity surfaces (contour plots) for two-variable interactions
- Calculate and visualize breakeven prices (oil, gas, or combined)
- Build scenario comparison matrices for management presentations
- Perform decision tree analysis for staged investments
- Create executive-ready sensitivity dashboards

## Related Skills

- **npv-analyzer**: Basic NPV and IRR calculations, Monte Carlo simulation
- **production-forecaster**: Decline curve analysis for production inputs
- **hse-risk-analyzer**: Safety data for risk-adjusted economics
- **bsee-data-extractor**: Production data for economic modeling

## Sub-Skills

- [Spider Diagram Analysis (+4)](spider-diagram-analysis/SKILL.md)

## Sub-Skills

- [SensitivityParameter (+6)](sensitivityparameter/SKILL.md)
- [YAML Configuration](yaml-configuration/SKILL.md)
- [CLI Usage](cli-usage/SKILL.md)
- [Example: Complete Sensitivity Analysis](example-complete-sensitivity-analysis/SKILL.md)
- [Output Formats](output-formats/SKILL.md)
