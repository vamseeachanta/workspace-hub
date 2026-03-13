"""Tests for ETL base ABCs — verify contract enforcement."""

import pytest
from data.pipeline.base import Extractor, Transformer, Loader


class TestExtractorABC:
    def test_cannot_instantiate_without_extract(self):
        class BadExtractor(Extractor):
            def cache_key(self):
                return "k"

        with pytest.raises(TypeError):
            BadExtractor()

    def test_cannot_instantiate_without_cache_key(self):
        class BadExtractor(Extractor):
            def extract(self, force_refresh=False):
                return []

        with pytest.raises(TypeError):
            BadExtractor()

    def test_valid_subclass_instantiates(self):
        class GoodExtractor(Extractor):
            def extract(self, force_refresh=False):
                return [{"a": 1}]

            def cache_key(self):
                return "good"

        e = GoodExtractor()
        assert e.cache_key() == "good"
        assert e.extract() == [{"a": 1}]


class TestTransformerABC:
    def test_cannot_instantiate_without_transform(self):
        class BadTransformer(Transformer):
            pass

        with pytest.raises(TypeError):
            BadTransformer()

    def test_valid_subclass_instantiates(self):
        import pandas as pd

        class GoodTransformer(Transformer):
            def transform(self, raw):
                return pd.DataFrame(raw)

        t = GoodTransformer()
        df = t.transform([{"x": 1}])
        assert len(df) == 1


class TestLoaderABC:
    def test_cannot_instantiate_without_load(self):
        class BadLoader(Loader):
            def output_path(self):
                from pathlib import Path
                return Path("/tmp/out.csv")

        with pytest.raises(TypeError):
            BadLoader()

    def test_cannot_instantiate_without_output_path(self):
        class BadLoader(Loader):
            def load(self, df):
                from pathlib import Path
                return Path("/tmp/out.csv")

        with pytest.raises(TypeError):
            BadLoader()

    def test_valid_subclass_instantiates(self):
        from pathlib import Path

        class GoodLoader(Loader):
            def load(self, df):
                return Path("/tmp/out.csv")

            def output_path(self):
                return Path("/tmp/out.csv")

        lo = GoodLoader()
        assert lo.output_path() == Path("/tmp/out.csv")
