---
name: repo-readiness-key-conventions
description: 'Sub-skill of repo-readiness: Key Conventions (+4).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Key Conventions (+4)

## Key Conventions


- **Imports**: Use absolute imports from src/
- **Testing**: Write tests before implementation (TDD)
- **Data Loading**: Use relative paths from reports/
- **Error Handling**: Use custom exceptions in src/exceptions.py
- **Logging**: Use module-level logger = logging.getLogger(__name__)

## Common Patterns


1. **Data Pipeline**: load → validate → process → visualize → report
2. **Configuration**: YAML files in config/input/ directory
3. **Execution**: Bash scripts in scripts/ directory
4. **Reporting**: HTML with Plotly in reports/ directory

## Recent Changes (Last 7 Days)


- Refactored NPV calculation to support multiple discount rates
- Added new marine safety incident categorization
- Updated BSEE data extractor for 2024 format
- Enhanced error handling in data validation

## Known Issues


- Issue #42: Slow performance on files >100MB (workaround documented)
- Issue #38: Timezone handling in date parsing (fix in progress)

## Quick Reference


- Main entry point: `scripts/run_analysis.sh`
- Configuration: `config/input/<feature>.yaml`
- Documentation: `docs/README.md`
- Examples: `examples/`
```
