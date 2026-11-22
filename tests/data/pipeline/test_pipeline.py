"""Tests for PipelineOrchestrator — extract→transform→load chain."""

from pathlib import Path
from unittest.mock import MagicMock, call

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


@pytest.fixture(params=["extract", "transform", "load"])
def failed_stage(request, tmp_path):
    raw = [{"value": "sample"}]
    df = pd.DataFrame(raw)
    extractor = _make_extractor(raw_data=raw)
    transformer = _make_transformer(df=df)
    loader = _make_loader(out_path=tmp_path / "unused-output.csv")
    stage_calls = MagicMock()
    for stage, component in (
        ("extract", extractor),
        ("transform", transformer),
        ("load", loader),
    ):
        spy = MagicMock(wraps=getattr(component, stage))
        setattr(component, stage, spy)
        stage_calls.attach_mock(spy, stage)

    failure = RuntimeError(f"{request.param} failed")
    getattr(stage_calls, request.param).side_effect = failure
    # Contract: stop at the failing phase; these sequences are hand-written.
    expected_calls = {
        "extract": [call.extract(force_refresh=True)],
        "transform": [
            call.extract(force_refresh=True),
            call.transform(raw),
        ],
        "load": [
            call.extract(force_refresh=True),
            call.transform(raw),
            call.load(df),
        ],
    }[request.param]
    return extractor, transformer, loader, stage_calls, failure, expected_calls


@pytest.fixture
def checkpoint_files(tmp_path):
    # Synthetic prior success: record_count is 1 by hand-counting the single row
    # in failed_stage. Literal bytes avoid using production serializers as oracles.
    state_bytes = (
        b'{"pipeline_name": "test_pipe", "last_value": "previous-success", '
        b'"record_count": 1, "run_at": "previous-success"}\n'
    )
    manifest_bytes = (
        b"# Preserve this formatting as well as the checkpoint values.\n"
        b"pipelines:\n"
        b"  test_pipe:\n"
        b"    source_url: synthetic-source\n"
        b"    refresh_cadence: daily\n"
        b"    last_run: previous-success\n"
        b"    record_count: 1\n"
        b"    output_path: previous-output.csv\n"
    )
    state_path = tmp_path / "state" / "test_pipe.json"
    state_path.parent.mkdir()
    manifest_path = tmp_path / "manifest.yaml"
    state_path.write_bytes(state_bytes)
    manifest_path.write_bytes(manifest_bytes)
    return (state_path, state_bytes), (manifest_path, manifest_bytes)


class TestPipelineOrchestrator:
    def test_failed_stage_preserves_checkpoint(
        self, state, manifest, failed_stage, checkpoint_files
    ):
        """Checkpoint isolation excludes rollback of external loader mutations."""
        extractor, transformer, loader, stage_calls, failure, expected_calls = (
            failed_stage
        )
        orch = PipelineOrchestrator(
            extractor=extractor,
            transformer=transformer,
            loader=loader,
            state=state,
            manifest=manifest,
            pipeline_name="test_pipe",
            source_url="synthetic-source",
            refresh_cadence="daily",
        )

        with pytest.raises(RuntimeError) as caught:
            orch.run(force_refresh=True)

        assert caught.value is failure
        assert stage_calls.mock_calls == expected_calls
        for path, fixture_bytes in checkpoint_files:
            assert path.read_bytes() == fixture_bytes

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
