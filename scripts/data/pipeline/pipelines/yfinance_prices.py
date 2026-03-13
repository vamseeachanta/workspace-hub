"""yfinance prices pipeline — OHLCV data with fixture fallback."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, field_validator

from data.pipeline.base import Extractor, Transformer, Loader


class OHLCVRecord(BaseModel):
    """Schema for a single OHLCV price record."""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

    @field_validator("volume")
    @classmethod
    def volume_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("volume must be non-negative")
        return v


class YFinancePricesExtractor(Extractor):
    """Extract OHLCV data from yfinance or fixture fallback."""

    def __init__(
        self,
        tickers: List[str],
        fixture_path: Optional[Path] = None,
    ) -> None:
        self._tickers = tickers
        self._fixture_path = fixture_path

    def extract(self, force_refresh: bool = False) -> Dict[str, List[dict]]:
        """Return {ticker: [records]}. Uses fixture if yfinance unavailable."""
        try:
            import yfinance as yf
        except ImportError:
            yf = None

        if yf is None or self._fixture_path is not None:
            return self._extract_from_fixture()

        return self._extract_live(yf)

    def _extract_from_fixture(self) -> Dict[str, List[dict]]:
        data = json.loads(self._fixture_path.read_text())
        return {ticker: data for ticker in self._tickers}

    def _extract_live(self, yf: Any) -> Dict[str, List[dict]]:
        result = {}
        for ticker in self._tickers:
            t = yf.Ticker(ticker)
            hist = t.history(period="1y")
            records = []
            for date, row in hist.iterrows():
                records.append({
                    "date": str(date.date()),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                })
            result[ticker] = records
        return result

    def cache_key(self) -> str:
        return "yfinance_prices"


class YFinancePricesTransformer(Transformer):
    """Validate OHLCV records across all tickers."""

    def transform(self, raw: Dict[str, List[dict]]) -> pd.DataFrame:
        all_records = []
        for ticker, records in raw.items():
            for item in records:
                r = OHLCVRecord(**item)
                row = r.model_dump()
                row["ticker"] = ticker
                all_records.append(row)
        return pd.DataFrame(all_records)


class YFinancePricesLoader(Loader):
    """Write OHLCV data as CSV."""

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = Path(output_dir)

    def load(self, df: pd.DataFrame) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        out = self.output_path()
        df.to_csv(out, index=False)
        return out

    def output_path(self) -> Path:
        return self._output_dir / "yfinance_prices.csv"
