# WorldEnergyData Module Template

> Version: 1.0.0 | Author: WorldEnergyData Team | Updated: 2026-01-24

This document defines the flexible module structure for WorldEnergyData modules. Modules should follow this template to ensure consistency, maintainability, and proper integration with the common layer.

---

## Table of Contents

1. [Overview](#overview)
2. [Required Structure](#required-structure)
3. [Optional Structure](#optional-structure)
4. [Guidelines](#guidelines)
5. [Examples](#examples)
6. [Compliance Checklist](#compliance-checklist)

---

## Overview

WorldEnergyData modules follow a flexible structure that scales from minimal (single-purpose) to complex (multi-capability) modules. All modules share common patterns for:

- Exports (`__all__` declarations)
- Exception handling (inheriting from `common/exceptions.py`)
- Logging (using `common/logging.py`)
- Configuration (using `common/config.py`)

---

## Required Structure

Every module MUST have these components:

```
modules/<module_name>/
    __init__.py         # Module exports with __all__ declaration
    data/               # Data access layer
        __init__.py     # Data layer exports
```

### `__init__.py` - Module Entry Point

The module's `__init__.py` MUST:

1. Include a module docstring with description, version, and author
2. Define `__all__` with all public exports
3. Use direct re-exports from submodules (not submodule references)
4. Include `__version__` for versioned modules

**Pattern: Direct Re-exports**

```python
"""
Module Name - Brief Description

Longer description of what this module provides.

Version: 1.0.0
Author: WorldEnergyData Team
"""

from .core import (
    MainClass,
    helper_function,
    ModuleError,
)
from .data import (
    DataLoader,
    DataProcessor,
)

__version__ = "1.0.0"

__all__ = [
    # Core
    "MainClass",
    "helper_function",
    "ModuleError",
    # Data
    "DataLoader",
    "DataProcessor",
    # Metadata
    "__version__",
]
```

### `data/` - Data Access Layer

The data layer handles all data operations:

- Loading from files, APIs, or databases
- Caching mechanisms
- Data transformation and normalization
- Schema validation

```
data/
    __init__.py         # Data layer exports
    loaders.py          # Data loading functions/classes
    processors.py       # Data transformation
    cache/              # Caching implementation (optional)
        __init__.py
        file_cache.py
```

---

## Optional Structure

Add these directories based on module complexity and needs:

### `core/` - Core Business Logic

Use when module has substantial domain logic separate from data access.

```
core/
    __init__.py         # Core exports
    models.py           # Domain models/dataclasses
    services.py         # Business logic services
    calculations.py     # Domain-specific calculations
```

### `analysis/` - Analysis Functions

Use for modules that perform data analysis, aggregation, or computation.

```
analysis/
    __init__.py         # Analysis exports
    metrics.py          # Metric calculations
    aggregators.py      # Data aggregation
    forecasting.py      # Predictive analysis
```

### `reports/` - Report Generation

Use for modules that produce output reports (HTML, Excel, PDF).

```
reports/
    __init__.py         # Report exports
    generators.py       # Report generation logic
    templates/          # Report templates
        __init__.py
        base_template.py
    exporters/          # Export format handlers
        __init__.py
        excel_exporter.py
        html_exporter.py
```

### `utils/` - Module-Specific Utilities

Use for utilities specific to this module (not cross-cutting concerns).

```
utils/
    __init__.py         # Utils exports
    formatters.py       # Module-specific formatters
    validators.py       # Module-specific validators
    helpers.py          # Other helper functions
```

### `adapters/` - External System Adapters

Use for integration with external APIs or other modules.

```
adapters/
    __init__.py         # Adapter exports
    external_api.py     # External API adapter
    other_module.py     # Cross-module adapter
```

### `cli.py` - Module CLI Commands

Use when module needs CLI commands. These become subcommands of the unified CLI.

```python
"""
Module CLI Commands

Provides command-line interface for module operations.
Integrates with unified worldenergydata CLI.
"""

import click
from worldenergydata.common import get_logger

logger = get_logger(__name__)


@click.group()
def cli():
    """Module name - brief description."""
    pass


@cli.command()
@click.option("--option", "-o", help="Description")
def command_name(option: str):
    """Command description."""
    # Implementation
    pass


# Export for unified CLI integration
__all__ = ["cli"]
```

---

## Guidelines

### 1. Use Common Layer for Cross-Cutting Concerns

**DO use common layer:**

```python
from worldenergydata.common import get_logger, WorldEnergyDataError
from worldenergydata.common.config import get_settings
from worldenergydata.common.constants import EnergyUnits
```

**DO NOT create module-specific versions:**

```python
# BAD - Don't do this
import logging
logger = logging.getLogger(__name__)  # Use get_logger instead

# BAD - Don't do this
class MyModuleError(Exception):  # Inherit from common exceptions
    pass
```

### 2. Exception Hierarchy

All module-specific exceptions MUST inherit from common exceptions:

```python
from worldenergydata.common.exceptions import ModuleError, DataError

class BSEEError(ModuleError):
    """BSEE module-specific errors."""
    default_code = "BSEE_ERROR"
    module_name = "bsee"

class BSEEDataError(DataError):
    """BSEE data-related errors."""
    default_code = "BSEE_DATA_ERROR"
```

### 3. `__all__` Declaration Pattern

Use the **direct re-export pattern** - export actual symbols, not submodule references:

```python
# CORRECT - Direct re-exports
from .data import DataLoader, DataProcessor

__all__ = [
    "DataLoader",      # Actual class
    "DataProcessor",   # Actual class
]

# INCORRECT - Submodule references
__all__ = [
    "data",           # Don't export submodules
    "core",           # Export their contents instead
]
```

### 4. Logging

Use the common logging facility:

```python
from worldenergydata.common import get_logger

logger = get_logger(__name__)

def my_function():
    logger.info("Operation started", extra={"context": "value"})
```

### 5. Configuration

Use common configuration for cross-module settings. Module-specific config goes in `data/config/`:

```python
# Cross-module settings
from worldenergydata.common.config import get_settings

settings = get_settings()
cache_dir = settings.cache_dir

# Module-specific config
from .data.config import ModuleConfig

config = ModuleConfig.load("config.yaml")
```

### 6. No Circular Imports

Structure imports to avoid circular dependencies:

- `data/` should not import from `analysis/`
- `core/` should not import from `reports/`
- Use dependency injection for cross-layer dependencies

---

## Examples

### Minimal Module: `reporting`

A simple module with just templates and utilities.

```
modules/reporting/
    __init__.py
    templates/
        __init__.py
        plotly_report_template.py
    utils/
        __init__.py
        path_utils.py
```

**`__init__.py`:**

```python
"""
Reporting utilities and templates for WorldEnergyData.
"""

__all__ = ["templates", "utils"]
```

### Standard Module: `fdas`

A typical module with core logic, data, analysis, and reports.

```
modules/fdas/
    __init__.py
    core/
        __init__.py
        financial.py
        config.py
    data/
        __init__.py
        production.py
        drilling.py
    analysis/
        __init__.py
        cashflow.py
    reports/
        __init__.py
        excel_generator.py
    adapters/
        __init__.py
        bsee_adapter.py
```

**`__init__.py`:**

```python
"""
FDAS (Field Development Analysis System) Module

Provides comprehensive financial analysis capabilities for deepwater field
development, including NPV/MIRR calculations, cashflow modeling, and
integration with BSEE data sources.

Version: 1.0.0
Author: WorldEnergyData Team
"""

from .core import (
    excel_like_mirr,
    calculate_npv,
    calculate_irr,
    calculate_all_metrics,
    FinancialCalculationError,
    AssumptionsManager,
    PriceDeckManager,
    classify_dev_system_by_depth,
    ConfigurationError,
)
from .adapters import (
    BseeAdapter,
    LeaseMapping,
    AdapterError,
)

__version__ = '1.0.0'

__all__ = [
    # Core financial
    'excel_like_mirr',
    'calculate_npv',
    'calculate_irr',
    'calculate_all_metrics',
    'FinancialCalculationError',
    # Configuration
    'AssumptionsManager',
    'PriceDeckManager',
    'classify_dev_system_by_depth',
    'ConfigurationError',
    # Adapters
    'BseeAdapter',
    'LeaseMapping',
    'AdapterError',
    # Metadata
    '__version__',
]
```

### Complex Module: `bsee`

A large module with multiple subsystems, CLIs, and legacy components.

```
modules/bsee/
    __init__.py
    data/
        __init__.py
        cache/
            __init__.py
            file_cache.py
        config/
            __init__.py
            sources.yaml
        enhanced/
            __init__.py
        processors/
            __init__.py
            normalizer.py
        scrapers/
            __init__.py
            war_scraper.py
            production_scraper.py
    analysis/
        __init__.py
        financial/
            __init__.py
            npv.py
        well_data_verification/
            __init__.py
            cli.py
            engine/
                __init__.py
            audit/
                __init__.py
    reports/
        __init__.py
        comprehensive/
            __init__.py
            cli.py
            aggregators/
            exporters/
            templates/
            visualizations/
    paleowells/
        __init__.py
        cli.py
    components/
        # Shared UI/report components
```

**Key patterns in complex modules:**

1. Subsystems have their own `cli.py` files
2. Nested directories for related functionality
3. `__init__.py` at every level with appropriate exports
4. Separate `config/` under `data/` for source configurations

---

## Compliance Checklist

Use this checklist when creating or reviewing modules:

### Required Elements

- [ ] `__init__.py` exists at module root
- [ ] `__init__.py` has docstring with description
- [ ] `__all__` is defined with explicit exports
- [ ] `__all__` uses direct re-exports (not submodule names)
- [ ] `data/` directory exists with `__init__.py`

### Common Layer Integration

- [ ] Uses `get_logger(__name__)` for logging (not raw `logging`)
- [ ] Custom exceptions inherit from `common.exceptions` hierarchy
- [ ] Uses `common.config.Settings` for cross-module configuration
- [ ] No duplicate logging configuration

### Code Organization

- [ ] No circular imports between directories
- [ ] Each `__init__.py` exports only its layer's public API
- [ ] CLI commands are in `cli.py` (not scattered across files)
- [ ] Tests mirror source structure in `tests/` directory

### Documentation

- [ ] Module docstring describes purpose and usage
- [ ] Public functions have docstrings
- [ ] Complex logic has inline comments
- [ ] `__version__` defined for versioned modules

### Best Practices

- [ ] Type hints on all public functions
- [ ] Error handling with appropriate exception types
- [ ] No hardcoded paths (use configuration)
- [ ] No sensitive data in code

---

## Module Registration

To integrate a new module with the package:

1. **Create module structure** following this template

2. **Add to modules `__init__.py`** (if exists):

   ```python
   from . import new_module
   ```

3. **Register CLI** in unified CLI entry point:

   ```python
   from worldenergydata.new_module.cli import cli as new_module_cli
   main.add_command(new_module_cli, name="new-module")
   ```

4. **Add tests** in `tests/modules/new_module/`

5. **Update documentation** in `.claude/docs/` if needed

---

## Version History

| Version | Date       | Changes                                    |
|---------|------------|-------------------------------------------|
| 1.0.0   | 2026-01-24 | Initial template                          |
