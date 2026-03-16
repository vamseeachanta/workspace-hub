---
name: data-validation-reporter-best-practices
description: 'Sub-skill of data-validation-reporter: Best Practices.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


1. **Configuration Management**:
   - Store validation rules in YAML (version controlled)
   - Use environment-specific configs (dev/staging/prod)
   - Document validation thresholds

2. **Logging**:
   - Enable DEBUG level during development
   - Use INFO level in production
   - Log all validation failures

3. **Reporting**:
   - Generate reports for all production data loads
   - Archive reports with timestamps
   - Include reports in data lineage

4. **Quality Gates**:
   - Set minimum quality score thresholds
   - Block pipelines on validation failures
   - Alert on quality degradation
