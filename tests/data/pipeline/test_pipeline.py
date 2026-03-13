"""Tests for PipelineOrchestrator — extract→transform→load chain."""

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest
from data.pipeline.base import Extractor, Transformer, Loader
from data.pipeline.manifest import ManifestManager
from data.pipeline.pipeline import PipelineOrchestrator
from data.pipeline.state import PipelineState


def _make_extractor(raw_data=None, key="test_pipe"):
    class StubExtractor(Extractor):
        def extract(self, force_refresh=False):
            return raw_data or [{"a": 1}]

        def cache_key(self):
            return key

    return StubExtractor()


def _make_transformer(df=None):
    class StubTransformer(Transformer):
        def transform(self, raw):
            return df if df is not None else pd.DataFrame(raw)

    return StubTransformer()


def _make_loader(out_path=None):
    _path = out_path or Path("/tmp/test_out.csv")

    class StubLoader(Loader):
        def load(self, df):
            return _path

        def output_path(self):
            return _path

    return StubLoader()


@pytest.fixture
def state(tmp_path):
    return PipelineState(tmp_path / "state")


@pytest.fixture
def manifest(tmp_path):
    return ManifestManager(tmp_path / "manifest.yaml")


class TestPipelineOrchestrator:
    def test_run_executes_full_etl_chain(self, state, manifest):
        raw = [{"x": 10}]
        df = pd.DataFrame(raw)
        out = Path("/tmp/output.csv")

        orch = PipelineOrchestrator(
            extractor=_make_extractor(raw_data=raw),
            transformer=_make_transformer(df=df),
            loader=_make_loader(out_path=out),
            state=state,
            manifest=manifest,
            pipeline_name="test_pipe",
            source_url="https://example.com",
            refresh_cadence="daily",
        )
        result = orch.run(force_refresh=True)

        assert result["skipped"] is False
        assert result["record_count"] == 1
        assert result["output_path"] == str(out)

    def test_run_updates_state(self, state, manifest):
        orch = PipelineOrchestrator(
            extractor=_make_extractor(key="my_pipe"),
            transformer=_make_transformer(),
            loader=_make_loader(),
            state=state,
            manifest=manifest,
            pipeline_name="my_pipe",
            source_url="url",
            refresh_cadence="daily",
        )
        orch.run(force_refresh=True)

        s = state.get("my_pipe")
        assert s is not None
        assert s["record_count"] == 1

    def test_run_updates_manifest(self, state, manifest):
        orch = PipelineOrchestrator(
            extractor=_make_extractor(),
            transformer=_make_transformer(),
            loader=_make_loader(),
            state=state,
            manifest=manifest,
            pipeline_name="test_pipe",
            source_url="https://example.com",
            refresh_cadence="weekly",
        )
        orch.run(force_refresh=True)

        m = manifest.read()
        assert "test_pipe" in m["pipelines"]
        assert m["pipelines"]["test_pipe"]["record_count"] == 1

    def test_skip_when_cache_fresh(self, state, manifest):
        # Pre-populate state with recent run
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        state.save("test_pipe", last_value="v1", record_count=5, run_at=now)

        orch = PipelineOrchestrator(
            extractor=_make_extractor(),
            transformer=_make_transformer(),
            loader=_make_loader(),
            state=state,
            manifest=manifest,
            pipeline_name="test_pipe",
            source_url="url",
            refresh_cadence="daily",
            ttl_hours=24,
        )
        result = orch.run(force_refresh=False)
        assert result["skipped"] is True

    def test_force_refresh_overrides_cache(self, state, manifest):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        state.save("test_pipe", last_value="v1", record_count=5, run_at=now)

        orch = PipelineOrchestrator(
            extractor=_make_extractor(),
            transformer=_make_transformer(),
            loader=_make_loader(),
            state=state,
            manifest=manifest,
            pipeline_name="test_pipe",
            source_url="url",
            refresh_cadence="daily",
            ttl_hours=24,
        )
        result = orch.run(force_refresh=True)
        assert result["skipped"] is False

    def test_run_with_empty_dataframe(self, state, manifest):
        empty_df = pd.DataFrame()
        orch = PipelineOrchestrator(
            extractor=_make_extractor(raw_data=[]),
            transformer=_make_transformer(df=empty_df),
            loader=_make_loader(),
            state=state,
            manifest=manifest,
            pipeline_name="test_pipe",
            source_url="url",
            refresh_cadence="daily",
        )
        result = orch.run(force_refresh=True)
        assert result["record_count"] == 0
