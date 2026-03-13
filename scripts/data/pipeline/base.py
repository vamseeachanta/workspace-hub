"""ETL base classes — abstract contracts for extract, transform, load."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class Extractor(ABC):
    """Fetch raw data from an external source."""

    @abstractmethod
    def extract(self, force_refresh: bool = False) -> Any:
        """Return raw data (JSON list, bytes, etc).

        Skip fetch if cache is fresh unless force_refresh=True.
        """

    @abstractmethod
    def cache_key(self) -> str:
        """Unique key for incremental state tracking."""


class Transformer(ABC):
    """Validate and reshape raw data into a DataFrame."""

    @abstractmethod
    def transform(self, raw: Any) -> pd.DataFrame:
        """Transform raw extracted data.

        Raises ValidationError on unexpected schema.
        """


class Loader(ABC):
    """Write transformed data to the standard output location."""

    @abstractmethod
    def load(self, df: pd.DataFrame) -> Path:
        """Write df to disk. Return output path."""

    @abstractmethod
    def output_path(self) -> Path:
        """Return the canonical output file path."""
