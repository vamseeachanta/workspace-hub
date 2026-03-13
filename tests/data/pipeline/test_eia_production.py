"""Tests for EIA production pipeline — mock HTTP, schema validation."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from data.pipeline.pipelines.eia_production import (
    EIAProductionExtractor,
    EIAProductionLoader,
    EIAProductionRecord,
    EIAProductionTransformer,
)

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def eia_response():
    return json.loads((FIXTURES / "eia_response.json").read_text())


class TestEIAProductionRecord:
    def test_valid_record(self):
        r = EIAProductionRecord(
            period="2026-02-28", series_id="PET.WCRSTUS1.W", value=12500.5
        )
        assert r.period == "2026-02-28"
        assert r.value == 12500.5

    def test_null_value_accepted(self):
        r = EIAProductionRecord(
            period="2026-02-07", series_id="PET.WCRSTUS1.W", value=None
        )
        assert r.value is None

    def test_invalid_period_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            EIAProductionRecord(period="", series_id="X", value=1.0)


class TestEIAProductionExtractor:
    def test_extract_calls_client(self, eia_response):
        mock_client = MagicMock()
        mock_client.fetch_petroleum_weekly.return_value = eia_response
        extractor = EIAProductionExtractor(client=mock_client)

        result = extractor.extract(force_refresh=True)
        assert len(result) == 5
        mock_client.fetch_petroleum_weekly.assert_called_once()

    def test_cache_key(self):
        extractor = EIAProductionExtractor(client=MagicMock())
        assert extractor.cache_key() == "eia_production"


class TestEIAProductionTransformer:
    def test_transform_valid_records(self, eia_response):
        t = EIAProductionTransformer()
        df = t.transform(eia_response)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert "period" in df.columns
        assert "value" in df.columns

    def test_transform_rejects_bad_schema(self):
        from pydantic import ValidationError

        t = EIAProductionTransformer()
        bad_data = [{"wrong_field": "x"}]
        with pytest.raises(ValidationError):
            t.transform(bad_data)


class TestEIAProductionLoader:
    def test_load_writes_jsonl(self, tmp_path):
        out = tmp_path / "eia_petroleum_weekly.jsonl"
        loader = EIAProductionLoader(output_dir=tmp_path)
        df = pd.DataFrame(
            [{"period": "2026-02-28", "series_id": "X", "value": 1.0}]
        )
        result_path = loader.load(df)
        assert result_path == out
        assert out.exists()
        lines = out.read_text().strip().split("\n")
        assert len(lines) == 1

    def test_output_path(self, tmp_path):
        loader = EIAProductionLoader(output_dir=tmp_path)
        assert loader.output_path().name == "eia_petroleum_weekly.jsonl"
