---
name: api-integration
version: 1.0.0
category: data
description: Integrate offshore engineering software APIs with mock testing for OrcaFlex,
  AQWA, and WAMIT
type: reference
capabilities: []
requires: []
tags: []
---

# Api Integration

## When to Use This Skill

Use this skill when you need to:
- Integrate with OrcaFlex Python API
- Integrate with ANSYS AQWA or WAMIT
- Create mock APIs for testing without software licenses
- Build automation workflows for marine analysis software
- Develop robust error handling for API calls
- Implement batch processing with external software APIs
- Create abstraction layers over multiple analysis tools

## Core Knowledge Areas

### 1. OrcaFlex API Integration

Working with OrcaFlex Python API:

```python
import os
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Mock OrcaFlex API for testing without license

*See sub-skills for full details.*
### 2. Abstract API Interface Pattern

Creating abstraction layer for multiple tools:

```python
class MarineAnalysisAPI(ABC):
    """Abstract base class for marine analysis software APIs."""

    @abstractmethod
    def create_model(self, config: dict) -> Any:
        """Create new analysis model."""
        pass

*See sub-skills for full details.*
### 3. Mock Testing Strategy

Testing without software licenses:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

class TestOrcaFlexIntegration:
    """Test suite for OrcaFlex integration using mocks."""


*See sub-skills for full details.*
### 4. Error Handling and Retry Logic

Robust error handling for API calls:

```python
import time
from functools import wraps
from typing import Callable, Any, Optional

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,

*See sub-skills for full details.*
### 5. Batch Processing with APIs

Automate multiple analyses:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import pandas as pd

class BatchAnalysisRunner:
    """
    Run batch analyses using marine analysis APIs.

*See sub-skills for full details.*

## Complete Examples

### Example 1: Multi-Tool Integration Workflow

```python
from pathlib import Path
import numpy as np

def multi_tool_analysis_workflow(
    geometry_file: Path,
    analysis_config: dict,
    output_dir: Path
) -> dict:
    """

*See sub-skills for full details.*

## Resources

### OrcaFlex API

- **Documentation**: OrcFxAPI Python documentation (in OrcaFlex installation)
- **Examples**: OrcaFlex → Examples → Python folder
- **Support**: support@orcina.com
### ANSYS AQWA

- **ANSYS ACT**: Application Customization Toolkit for scripting
- **PyAnsys**: https://github.com/pyansys
- **Documentation**: ANSYS Help → AQWA → Programmer's Guide
### Testing

- **pytest**: https://docs.pytest.org/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html
- **Mock Testing Best Practices**: Various online resources
### Python API Design

- **PEP 8**: Python style guide
- **Design Patterns**: Gang of Four patterns
- **Abstract Base Classes**: Python ABC module documentation

---

**Use this skill for:** Expert API integration with marine analysis software, mock testing strategies, and automation workflows with robust error handling.

## Sub-Skills

- [1. API Availability Checking (+2)](1-api-availability-checking/SKILL.md)
