"""EIA petroleum production pipeline — wraps EIAFeedClient."""

import json
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd
from pydantic import BaseModel, field_validator

from data.pipeline.base import Extractor, Transformer, Loader


class EIAProductionRecord(BaseModel):
    """Schema for a single EIA petroleum weekly record."""

    period: str
    series_id: str
    value: Optional[float] = None

    @field_validator("period")
    @classmethod
    def period_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("period must not be empty")
        return v.strip()


class EIAProductionExtractor(Extractor):
    """Extract petroleum weekly data via EIAFeedClient."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def extract(self, force_refresh: bool = False) -> List[dict]:
        return self._client.fetch_petroleum_weekly()

    def cache_key(self) -> str:
        return "eia_production"


class EIAProductionTransformer(Transformer):
    """Validate and convert EIA records to DataFrame."""

    def transform(self, raw: List[dict]) -> pd.DataFrame:
        records = []
        for item in raw:
            r = EIAProductionRecord(
                period=item.get("period", ""),
                series_id=item.get("series-id", item.get("series_id", "")),
                value=item.get("value"),
            )
            records.append(r.model_dump())
        return pd.DataFrame(records)


class EIAProductionLoader(Loader):
    """Write EIA data as JSONL."""

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = Path(output_dir)

    def load(self, df: pd.DataFrame) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        out = self.output_path()
        with open(out, "w") as f:
            for _, row in df.iterrows():
                f.write(json.dumps(row.to_dict(), default=str) + "\n")
        return out

    def output_path(self) -> Path:
        return self._output_dir / "eia_petroleum_weekly.jsonl"
