"""Tests for yfinance prices pipeline — fixture fallback, schema validation."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from data.pipeline.pipelines.yfinance_prices import (
    OHLCVRecord,
    YFinancePricesExtractor,
    YFinancePricesLoader,
    YFinancePricesTransformer,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def ohlcv_data():
    return json.loads((FIXTURES / "yfinance_ohlcv.json").read_text())


class TestOHLCVRecord:
    def test_valid_record(self):
        r = OHLCVRecord(
            date="2026-01-02", open=150.0, high=152.5, low=149.5,
            close=151.0, volume=1000000,
        )
        assert r.close == 151.0

    def test_negative_volume_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OHLCVRecord(
                date="2026-01-02", open=150.0, high=152.5, low=149.5,
                close=151.0, volume=-1,
            )


class TestYFinancePricesExtractor:
    def test_fixture_fallback_when_no_yfinance(self, ohlcv_data):
        extractor = YFinancePricesExtractor(
            tickers=["AAPL"],
            fixture_path=FIXTURES / "yfinance_ohlcv.json",
        )
        # Force fixture mode
        result = extractor.extract(force_refresh=False)
        assert "AAPL" in result
        assert len(result["AAPL"]) == 5

    def test_cache_key(self):
        extractor = YFinancePricesExtractor(
            tickers=["AAPL", "MSFT"],
            fixture_path=FIXTURES / "yfinance_ohlcv.json",
        )
        assert extractor.cache_key() == "yfinance_prices"


class TestYFinancePricesTransformer:
    def test_transform_valid_data(self, ohlcv_data):
        t = YFinancePricesTransformer()
        raw = {"AAPL": ohlcv_data}
        df = t.transform(raw)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert "ticker" in df.columns
        assert "close" in df.columns

    def test_transform_multiple_tickers(self, ohlcv_data):
        t = YFinancePricesTransformer()
        raw = {"AAPL": ohlcv_data, "MSFT": ohlcv_data}
        df = t.transform(raw)
        assert len(df) == 10

    def test_transform_rejects_bad_record(self):
        from pydantic import ValidationError

        t = YFinancePricesTransformer()
        raw = {"BAD": [{"wrong": "data"}]}
        with pytest.raises(ValidationError):
            t.transform(raw)


class TestYFinancePricesLoader:
    def test_load_writes_csv_per_ticker(self, tmp_path):
        loader = YFinancePricesLoader(output_dir=tmp_path)
        df = pd.DataFrame([
            {"ticker": "AAPL", "date": "2026-01-02", "open": 150.0,
             "high": 152.5, "low": 149.5, "close": 151.0, "volume": 1000000},
        ])
        path = loader.load(df)
        assert path.exists()

    def test_output_path(self, tmp_path):
        loader = YFinancePricesLoader(output_dir=tmp_path)
        assert "yfinance_prices.csv" in str(loader.output_path())
