---
name: parallel-file-processor-core-components
description: 'Sub-skill of parallel-file-processor: Core Components (+5).'
version: 1.1.0
category: development
type: reference
scripts_exempt: true
---

# Core Components (+5)

## Core Components


```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    List, Dict, Any, Callable, Optional, Generator, TypeVar, Generic
)
from enum import Enum
import logging

logger = logging.getLogger(__name__)

*See sub-skills for full details.*

## File Scanner


```python
import fnmatch
from typing import List, Optional, Set, Generator
from pathlib import Path

class FileScanner:
    """
    Scan directories for files matching patterns.

    Supports glob patterns, extension filtering, and size limits.

*See sub-skills for full details.*

## Parallel Processor


```python
import time
from concurrent.futures import (
    ThreadPoolExecutor, ProcessPoolExecutor,
    as_completed, Future
)
from typing import Callable, TypeVar, Generic, List
import asyncio
from functools import partial


*See sub-skills for full details.*

## File Processor


```python
class FileProcessor:
    """
    High-level file processing with parallel execution.

    Combines scanning, filtering, and parallel processing.
    """

    def __init__(self,
                 scanner: FileScanner = None,

*See sub-skills for full details.*

## Progress Tracking


```python
from datetime import datetime, timedelta
import sys

class ProgressTracker:
    """Track and display processing progress."""

    def __init__(self,
                 total: int,
                 description: str = "Processing",

*See sub-skills for full details.*

## Result Aggregator


```python
import json

class ResultAggregator:
    """Aggregate and export batch processing results."""

    def __init__(self, batch_result: BatchResult):
        self.batch_result = batch_result

    def to_dataframe(self) -> pd.DataFrame:

*See sub-skills for full details.*
