---
name: yaml-workflow-executor-configuration-loader
description: 'Sub-skill of yaml-workflow-executor: Configuration Loader (+3).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Configuration Loader (+3)

## Configuration Loader


```python
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass

*See sub-skills for full details.*

## Workflow Router


```python
class WorkflowRouter:
    """Route tasks to appropriate handlers based on configuration."""

    def __init__(self):
        self.handlers = {}

    def register(self, task_name: str, handler_func):
        """Register a handler for a task type."""
        self.handlers[task_name] = handler_func

*See sub-skills for full details.*

## Handler Registration Pattern


```python
def register_handlers(router: WorkflowRouter):
    """Register all available task handlers."""

    @router.register('analyze_data')
    def analyze_data(config: WorkflowConfig):
        """Handler for data analysis tasks."""
        import pandas as pd

        # Load input

*See sub-skills for full details.*

## Main Executor


```python
def execute_workflow(yaml_path: str, overrides: Dict[str, Any] = None) -> Any:
    """
    Execute workflow from YAML configuration.

    Args:
        yaml_path: Path to YAML config file
        overrides: Optional parameter overrides

    Returns:

*See sub-skills for full details.*
