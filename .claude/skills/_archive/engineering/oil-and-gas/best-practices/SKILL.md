---
name: oil-and-gas-best-practices
description: 'Sub-skill of oil-and-gas: Best Practices.'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


### Data Quality

1. Always validate input data ranges against physical constraints
2. Check for missing or anomalous values before analysis
3. Apply appropriate data cleaning techniques
4. Document data sources and assumptions

### Analysis Workflow

1. Start with exploratory data analysis
2. Apply domain-specific correlations (Standing, Beggs-Brill, etc.)
3. Validate results against field analogues
4. Perform sensitivity analysis
5. Document uncertainties explicitly

### Safety and Environment

1. Follow HSE guidelines in all technical work
2. Consider environmental impact in design decisions
3. Apply risk assessment methodologies (bow-tie, HAZID/HAZOP)
4. Maintain regulatory compliance throughout

### Code Standards

1. Use industry-standard units (field or SI — be explicit)
2. Include unit conversion utilities
3. Implement robust error handling with physical constraint checks
4. Provide comprehensive docstrings
5. Follow PEP 8 style guide

### Response Standards When Providing Technical Solutions

1. Start with fundamentals: explain underlying principles before complex solutions
2. Use industry terminology with explanations where needed
3. Include calculations: show relevant equations and example calculations
4. Reference standards: cite applicable API, ISO, or regulatory standards
5. Consider safety: always prioritize HSE considerations in recommendations
