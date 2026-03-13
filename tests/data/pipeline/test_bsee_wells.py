"""Tests for BSEE wells pipeline — fixture CSV, Pydantic validation."""

from pathlib import Path

import pandas as pd
import pytest
from data.pipeline.pipelines.bsee_wells import (
    BSEEWellRecord,
    BSEEWellsExtractor,
    BSEEWellsLoader,
    BSEEWellsTransformer,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestBSEEWellRecord:
    def test_valid_record(self):
        r = BSEEWellRecord(
            api_well_number="177154103200",
            well_name="WELL A-1",
            area_code="GC",
            block_number="640",
            water_depth=7200.0,
            latitude=27.2123,
            longitude=-90.1234,
            status_code="PA",
        )
        assert r.area_code == "GC"
        assert r.water_depth == 7200.0

    def test_empty_well_name_becomes_none(self):
        r = BSEEWellRecord(
            api_well_number="177154103400",
            well_name="",
            area_code="WR",
            block_number="718",
            water_depth=6500.0,
        )
        assert r.well_name is None

    def test_optional_lat_lon(self):
        r = BSEEWellRecord(
            api_well_number="177154103400",
            well_name=None,
            area_code="WR",
            block_number="718",
            water_depth=6500.0,
        )
        assert r.latitude is None
        assert r.longitude is None


class TestBSEEWellsExtractor:
    def test_extract_from_local_csv(self):
        extractor = BSEEWellsExtractor(csv_path=FIXTURES / "bsee_wells_sample.csv")
        result = extractor.extract()
        assert isinstance(result, str)
        assert "WELL A-1" in result

    def test_cache_key(self):
        extractor = BSEEWellsExtractor(csv_path=FIXTURES / "bsee_wells_sample.csv")
        assert extractor.cache_key() == "bsee_wells"


class TestBSEEWellsTransformer:
    def test_transform_valid_csv(self):
        csv_text = (FIXTURES / "bsee_wells_sample.csv").read_text()
        t = BSEEWellsTransformer()
        df = t.transform(csv_text)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4
        assert "api_well_number" in df.columns

    def test_transform_rejects_missing_required_columns(self):
        from pydantic import ValidationError

        t = BSEEWellsTransformer()
        bad_csv = "WRONG_COL\nval\n"
        with pytest.raises((ValidationError, KeyError)):
            t.transform(bad_csv)


class TestBSEEWellsLoader:
    def test_load_writes_csv(self, tmp_path):
        loader = BSEEWellsLoader(output_dir=tmp_path)
        df = pd.DataFrame(
            [{"api_well_number": "X", "well_name": "Y", "area_code": "GC",
              "block_number": "1", "water_depth": 100.0}]
        )
        path = loader.load(df)
        assert path.exists()
        assert path.suffix == ".csv"

    def test_output_path(self, tmp_path):
        loader = BSEEWellsLoader(output_dir=tmp_path)
        assert loader.output_path().name == "bsee_wells.csv"
