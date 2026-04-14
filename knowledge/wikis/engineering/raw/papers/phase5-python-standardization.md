# Phase 5: Python 3.9+ Standardization Plan

**Date:** 2025-09-28
**Status:** In Progress
**Repositories to Update:** 18

## Executive Summary

Standardizing all repositories to Python >=3.9 as Python 3.8 reached end-of-life in October 2024. This ensures security, performance, and access to modern Python features.

## Repositories Requiring Updates

### Batch 1: Core Projects (6 repos)
- aceengineer-admin (no version specified)
- aceengineer-website (3.8 → 3.9)
- acma-projects (3.8 → 3.9)
- ai-native-traditional-eng (3.8 → 3.9)
- client_projects (3.8 → 3.9)
- doris (3.8 → 3.9)

### Batch 2: Energy & Industrial (6 repos)
- energy (3.8 → 3.9)
- frontierdeepwater (3.8 → 3.9)
- OGManufacturing (3.8 → 3.9)
- rock-oil-field (3.8 → 3.9)
- saipem (3.8 → 3.9)
- seanation (3.8 → 3.9)

### Batch 3: Miscellaneous Projects (6 repos)
- achantas-media (3.8 → 3.9)
- hobbies (3.8 → 3.9)
- pyproject-starter (3.8 → 3.9)
- sabithaandkrishnaestates (3.8 → 3.9)
- sd-work (3.8 → 3.9)
- teamresumes (3.8 → 3.9)

## Already Compliant (7 repos)
✅ aceengineercode (3.9+)
✅ investments (3.9+)
✅ achantas-data (3.9+)
✅ assetutilities (3.9+)
✅ assethold (3.9+)
✅ digitalmodel (3.9+)
✅ worldenergydata (3.9+)

## Updates Required

### 1. pyproject.toml
```toml
requires-python = ">=3.9"  # Update from >=3.8

[tool.black]
target-version = ['py39', 'py310', 'py311', 'py312']  # Update from py38

[tool.mypy]
python_version = "3.9"  # Update from 3.8
```

### 2. GitHub Actions Workflows
```yaml
python-version: ["3.9", "3.10", "3.11", "3.12"]  # Remove 3.8
```

### 3. UV Configuration (if present)
```toml
[tool.uv]
python = "3.11"  # Ensure modern version
```

## Benefits of Python 3.9+

1. **Security**: Python 3.8 EOL October 2024
2. **Performance**: ~10-15% faster than 3.8
3. **Features**:
   - Dictionary merge operators (|, |=)
   - Type hinting improvements
   - String methods removeprefix/removesuffix
   - Improved timezone support
   - Better performance for built-in types

## Implementation Strategy

1. Update configuration files
2. Verify no Python 3.8-specific code
3. Update CI/CD pipelines
4. Test with Python 3.9+
5. Commit changes

## Risk Assessment

- **Low Risk**: Configuration change only
- **Testing**: Existing tests validate compatibility
- **Rollback**: Simple revert if issues arise