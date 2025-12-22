# Standards & Compliance Documentation

This directory contains all documentation related to coding standards, compliance requirements, and best practices.

## Contents

### Coding Standards

| File | Description |
|------|-------------|
| [FILE_ORGANIZATION_STANDARDS.md](FILE_ORGANIZATION_STANDARDS.md) | File and folder organization rules |
| [LOGGING_STANDARDS.md](LOGGING_STANDARDS.md) | Logging format and requirements |
| [TESTING_FRAMEWORK_STANDARDS.md](TESTING_FRAMEWORK_STANDARDS.md) | Testing standards and coverage |
| [HTML_REPORTING_STANDARDS.md](HTML_REPORTING_STANDARDS.md) | Interactive HTML report requirements |

### Compliance

| File | Description |
|------|-------------|
| [COMPLIANCE_ENFORCEMENT.md](COMPLIANCE_ENFORCEMENT.md) | How compliance is enforced |
| [README_COMPLIANCE.md](README_COMPLIANCE.md) | README format compliance guide |

## Key Standards

### File Organization

- **NEVER** save files to root folder
- Use appropriate subdirectories: `src/`, `tests/`, `docs/`, `config/`, `scripts/`
- Maximum 5 levels of nesting
- Module-driven naming (domain/business names)

### HTML Reporting

- **Interactive plots ONLY** (Plotly, Bokeh, Altair, D3.js)
- NO static matplotlib PNG/SVG exports
- CSV data with relative paths
- Store data in `/data/raw/`, `/data/processed/`, `/data/results/`

### Testing

- 80%+ code coverage required
- TDD mandatory (write tests first)
- No mock tests or mock data - use real repository data
- Unit, integration, and performance tests

### Logging

- Structured logging format
- Appropriate log levels
- No sensitive data in logs

## Related Documentation

- [AI Guidelines](../ai/) - AI agent workflow rules
- [Development Workflow](../workflow/) - Complete workflow process
- [Testing Module](../modules/testing/) - Detailed testing infrastructure

---

*Part of the workspace-hub documentation infrastructure*
