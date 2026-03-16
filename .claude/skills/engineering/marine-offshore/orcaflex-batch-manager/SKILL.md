---
name: orcaflex-batch-manager
description: Manage large-scale OrcaFlex batch processing with parallel execution,
  adaptive worker scaling, memory optimization, and progress tracking for efficient
  simulation campaigns.
version: 1.0.0
updated: 2026-01-17
category: engineering
triggers:
- batch processing
- parallel simulations
- batch manager
- run multiple models
- simulation campaign
- large batch
- parallel OrcaFlex
- job queue
capabilities: []
requires: []
see_also:
- orcaflex-batch-manager-version-metadata
- orcaflex-batch-manager-100-2026-01-17
- orcaflex-batch-manager-parallel-execution
- orcaflex-batch-manager-batch-results-json
tags: []
scripts_exempt: true
---

# Orcaflex Batch Manager

## When to Use

- Running large simulation campaigns (100+ cases)
- Parallel processing of multiple OrcaFlex models
- Sensitivity studies with many parameter combinations
- Operability matrices covering many sea states
- Multi-seed Monte Carlo simulations
- Overnight batch processing with monitoring

## Python API

### Basic Batch Processing

```python
from digitalmodel.orcaflex.universal.batch_processor import BatchProcessor
from pathlib import Path

def run_batch(input_dir: str, output_dir: str, max_workers: int = 20):
    """
    Run batch processing on OrcaFlex models.

    Args:
        input_dir: Directory containing model files

*See sub-skills for full details.*
### Adaptive Parallel Processing

```python
from digitalmodel.orcaflex.universal.batch_processor import BatchProcessor
from pathlib import Path
import psutil

class AdaptiveBatchProcessor(BatchProcessor):
    """Batch processor with adaptive resource management."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

*See sub-skills for full details.*
### Chunk-Based Processing

```python
from digitalmodel.orcaflex.universal.batch_processor import BatchProcessor
from pathlib import Path
import time

def process_in_chunks(
    input_dir: str,
    output_dir: str,
    chunk_size: int = 50,
    pause_seconds: int = 5

*See sub-skills for full details.*
### Progress Tracking and Checkpoints

```python
from digitalmodel.orcaflex.universal.batch_processor import BatchProcessor
from pathlib import Path
import json
import time

class CheckpointBatchProcessor(BatchProcessor):
    """Batch processor with checkpoint save/restore."""

    def __init__(self, checkpoint_file: str = "batch_checkpoint.json", **kwargs):

*See sub-skills for full details.*
### File Size Optimization

```python
from pathlib import Path
import os

def sort_by_file_size(files: list, reverse: bool = True) -> list:
    """
    Sort files by size for optimal processing order.

    Processing large files first with fewer workers,
    then small files with more workers.

*See sub-skills for full details.*
### Performance Metrics

```python
from dataclasses import dataclass, field
from typing import Dict, List
import time
import json

@dataclass
class BatchMetrics:
    """Track batch processing performance metrics."""


*See sub-skills for full details.*

## Related Skills

- [orcaflex-modeling](../orcaflex-modeling/SKILL.md) - Run OrcaFlex simulations
- [orcaflex-operability](../orcaflex-operability/SKILL.md) - Multi-sea-state campaigns
- [orcaflex-post-processing](../orcaflex-post-processing/SKILL.md) - Extract results
- [orcaflex-results-comparison](../orcaflex-results-comparison/SKILL.md) - Compare results

## References

- Python concurrent.futures documentation
- psutil system monitoring
- Source: `src/digitalmodel/modules/orcaflex/universal/batch_processor.py`
- Source: `src/digitalmodel/modules/orcaflex/orcaflex_parallel_analysis.py`

## Sub-Skills

- [Basic Batch Configuration (+1)](basic-batch-configuration/SKILL.md)
- [Resource Management (+2)](resource-management/SKILL.md)

## Sub-Skills

- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Version Metadata](version-metadata/SKILL.md)
- [[1.0.0] - 2026-01-17](100-2026-01-17/SKILL.md)
- [Parallel Execution (+1)](parallel-execution/SKILL.md)
- [Batch Results JSON (+1)](batch-results-json/SKILL.md)
