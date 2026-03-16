---
name: development-workflow-orchestrator-automatic-validation
description: 'Sub-skill of development-workflow-orchestrator: Automatic Validation.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Automatic Validation

## Automatic Validation


**HTML Reporting:**
```python
def validate_reporting_standards(config):
    """Ensure HTML reporting standards compliance."""
    if config['output']['visualization'] not in ['plotly', 'bokeh', 'altair', 'd3']:
        raise StandardsViolation(
            "HTML_REPORTING_STANDARDS.md violation: "
            "Must use interactive plots (Plotly, Bokeh, Altair, D3.js). "
            "Static matplotlib exports NOT ALLOWED."
        )

*See sub-skills for full details.*
