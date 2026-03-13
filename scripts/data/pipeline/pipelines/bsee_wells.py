"""BSEE wells pipeline — public CSV data with Pydantic validation."""

import io
from pathlib import Path
from typing import Optional

import pandas as pd
from pydantic import BaseModel, ConfigDict, field_validator

from data.pipeline.base import Extractor, Transformer, Loader


class BSEEWellRecord(BaseModel):
    """Schema for a BSEE well record."""

    model_config = ConfigDict(str_strip_whitespace=True)

    api_well_number: str
    well_name: Optional[str] = None
    area_code: str
    block_number: str
    water_depth: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status_code: Optional[str] = None

    @field_validator("well_name", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class BSEEWellsExtractor(Extractor):
    """Extract BSEE well data from a local CSV file."""

    def __init__(self, csv_path: Path) -> None:
        self._csv_path = Path(csv_path)

    def extract(self, force_refresh: bool = False) -> str:
        return self._csv_path.read_text()

    def cache_key(self) -> str:
        return "bsee_wells"


class BSEEWellsTransformer(Transformer):
    """Validate CSV rows against BSEEWellRecord schema."""

    _COLUMN_MAP = {
        "API_WELL_NUMBER": "api_well_number",
        "WELL_NAME": "well_name",
        "AREA_CODE": "area_code",
        "BLOCK_NUMBER": "block_number",
        "WATER_DEPTH": "water_depth",
        "LATITUDE": "latitude",
        "LONGITUDE": "longitude",
        "STATUS_CODE": "status_code",
    }

    def transform(self, raw: str) -> pd.DataFrame:
        df = pd.read_csv(io.StringIO(raw), dtype={"API_WELL_NUMBER": str, "BLOCK_NUMBER": str})
        df = df.rename(columns=self._COLUMN_MAP)
        records = []
        for _, row in df.iterrows():
            r = BSEEWellRecord(**{
                k: (None if pd.isna(v) else v)
                for k, v in row.to_dict().items()
                if k in BSEEWellRecord.model_fields
            })
            records.append(r.model_dump())
        return pd.DataFrame(records)


class BSEEWellsLoader(Loader):
    """Write validated BSEE well data as CSV."""

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = Path(output_dir)

    def load(self, df: pd.DataFrame) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        out = self.output_path()
        df.to_csv(out, index=False)
        return out

    def output_path(self) -> Path:
        return self._output_dir / "bsee_wells.csv"
