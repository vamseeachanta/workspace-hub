---
name: sphinx-4-autodoc-automatic-api-documentation
description: 'Sub-skill of sphinx: 4. Autodoc - Automatic API Documentation.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# 4. Autodoc - Automatic API Documentation

## 4. Autodoc - Automatic API Documentation


```python
# src/mypackage/core.py

"""
Core module for MyPackage.

This module provides the main classes and functions for
data processing and analysis.

Example:
    Basic usage of the module::

        from mypackage.core import DataProcessor
        processor = DataProcessor()
        result = processor.process(data)

"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path


class DataProcessor:
    """
    A class for processing and analyzing data.

    This processor supports multiple data formats and provides
    methods for validation, transformation, and export.

    Attributes:
        config: Configuration dictionary for the processor.
        verbose: Whether to print verbose output.
        _cache: Internal cache for processed results.

    Example:
        >>> processor = DataProcessor(verbose=True)
        >>> processor.load("data.csv")
        >>> result = processor.process()
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        verbose: bool = False
    ) -> None:
        """
        Initialize the DataProcessor.

        Args:
            config: Optional configuration dictionary. If not provided,
                defaults will be used. Keys include:
                - ``max_rows``: Maximum rows to process (default: 10000)
                - ``encoding``: File encoding (default: 'utf-8')
                - ``delimiter``: CSV delimiter (default: ',')
            verbose: If True, print progress information during
                processing. Defaults to False.

        Raises:
            ValueError: If config contains invalid keys.

        Example:
            >>> config = {'max_rows': 5000, 'encoding': 'utf-8'}
            >>> processor = DataProcessor(config=config, verbose=True)
        """
        self.config = config or {}
        self.verbose = verbose
        self._cache: Dict[str, Any] = {}

    def load(
        self,
        path: Union[str, Path],
        *,
        validate: bool = True
    ) -> 'DataProcessor':
        """
        Load data from a file.

        Supports CSV, JSON, and Parquet formats. The format is
        automatically detected from the file extension.

        Args:
            path: Path to the data file. Can be a string or
                :class:`pathlib.Path` object.
            validate: Whether to validate data after loading.
                Defaults to True.

        Returns:
            Self for method chaining.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is not supported.

        Example:
            >>> processor = DataProcessor()
            >>> processor.load("input.csv", validate=True)
            <DataProcessor object>

        See Also:
            :meth:`save`: Save processed data to file.
            :meth:`validate`: Validate loaded data.

        Note:
            Large files (>1GB) may require additional memory.
            Consider using chunked processing for such files.
        """
        # Implementation here
        return self

    def process(
        self,
        operations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process the loaded data with specified operations.

        Args:
            operations: List of operation names to apply.
                Available operations:
                - ``'clean'``: Remove null values
                - ``'normalize'``: Normalize numeric columns
                - ``'aggregate'``: Compute aggregations
                If None, all operations are applied.

        Returns:
            Dictionary containing:
            - ``data``: Processed data
            - ``stats``: Processing statistics
            - ``errors``: List of any errors encountered

        Raises:
            RuntimeError: If no data has been loaded.

        Warning:
            This method modifies the internal data state.
            Use :meth:`copy` first if you need the original.

        Example:
            >>> processor.load("data.csv")
            >>> result = processor.process(['clean', 'normalize'])
            >>> print(result['stats'])
            {'rows_processed': 1000, 'time_ms': 42}
        """
        return {'data': None, 'stats': {}, 'errors': []}

    def save(
        self,
        path: Union[str, Path],
        format: str = 'csv'
    ) -> None:
        """
        Save processed data to a file.

        Args:
            path: Output file path.
            format: Output format. One of:
                - ``'csv'``: Comma-separated values
                - ``'json'``: JSON format
                - ``'parquet'``: Apache Parquet format

        Raises:
            ValueError: If format is not supported.
            IOError: If file cannot be written.

        Example:
            >>> processor.process()
            >>> processor.save("output.csv", format='csv')
        """
        pass


def calculate_metrics(
    data: List[float],
    *,
    include_variance: bool = False
) -> Dict[str, float]:
    """
    Calculate statistical metrics for a list of values.

    This function computes common statistical measures
    for the provided data.

    Args:
        data: List of numeric values to analyze.

*Content truncated — see parent skill for full reference.*
