---
name: validate
type: command
plugin: data
source: https://github.com/anthropics/knowledge-work-plugins
---

# /validate - QA an Analysis

Review an analysis for accuracy, methodology, and potential biases before sharing with stakeholders.

## Usage

```
/validate <analysis to review>
```

## Workflow

### 1. Receive the Analysis

Accept analysis in any form:
- SQL queries and their results
- Charts and visualizations
- Written findings and conclusions
- Notebooks or code

### 2. Review Dimensions

Evaluate across seven dimensions:

**Methodology**
- Is the question well-framed?
- Is the right data source used?
- Is the population correctly defined?
- Are metrics clearly defined?
- Are comparisons fair (same time periods, same definitions)?

**Analytical Errors**
- Check for common pitfalls: join explosions, survivorship bias, Simpson's paradox
- Verify data completeness and null handling
- Check for aggregation errors (average of averages)
- Verify time period alignment

**Calculations**
- Spot-check key numbers
- Verify subtotals sum correctly
- Check percentage calculations
- Verify filter consistency

**Visualizations**
- Bar charts start at zero
- Axes are appropriate and labeled
- Scales are consistent across panels
- Charts are not misleading

**Narrative**
- Do conclusions follow from the evidence?
- Are limitations acknowledged?
- Are alternative explanations considered?

**Improvements**
- Suggest additional analyses that would strengthen findings
- Identify missing context or comparisons

**Confidence Rating**
- **Ready to share**: Analysis is sound, conclusions supported
- **Share with caveats**: Generally sound but note specific limitations
- **Needs revision**: Significant issues that should be addressed first

### 3. Output

Generate a validation report with:
- Issues found, categorized by severity (high/medium/low)
- Verified calculations
- Visualization concerns
- Suggested enhancements
- Required caveats for stakeholders
- Overall confidence rating

## Tips

- Run validation before any high-stakes presentation
- Focus on the highest-impact issues first
- Be specific about what needs fixing and how
