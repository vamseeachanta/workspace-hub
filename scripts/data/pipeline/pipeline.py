"""PipelineOrchestrator — extract→transform→load with incremental skip."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from data.pipeline.base import Extractor, Transformer, Loader
from data.pipeline.manifest import ManifestManager
from data.pipeline.state import PipelineState


class PipelineOrchestrator:
    """Run extract→transform→load chain with state tracking and manifest."""

    def __init__(
        self,
        extractor: Extractor,
        transformer: Transformer,
        loader: Loader,
        state: PipelineState,
        manifest: ManifestManager,
        pipeline_name: str,
        source_url: str,
        refresh_cadence: str,
        ttl_hours: float = 0,
    ) -> None:
        self._extractor = extractor
        self._transformer = transformer
        self._loader = loader
        self._state = state
        self._manifest = manifest
        self._name = pipeline_name
        self._source_url = source_url
        self._refresh_cadence = refresh_cadence
        self._ttl_hours = ttl_hours

    def run(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Execute the pipeline. Returns result dict."""
        if not force_refresh and self._is_fresh():
            return {"skipped": True, "record_count": 0, "output_path": ""}

        raw = self._extractor.extract(force_refresh=force_refresh)
        df = self._transformer.transform(raw)
        out_path = self._loader.load(df)

        record_count = len(df)
        now = datetime.now(timezone.utc).isoformat()

        self._state.save(
            pipeline_name=self._name,
            last_value=now,
            record_count=record_count,
            run_at=now,
        )
        self._manifest.update(
            pipeline_name=self._name,
            source_url=self._source_url,
            refresh_cadence=self._refresh_cadence,
            last_run=now,
            record_count=record_count,
            output_path=str(out_path),
        )

        return {
            "skipped": False,
            "record_count": record_count,
            "output_path": str(out_path),
        }

    def _is_fresh(self) -> bool:
        """Check if last run is within TTL."""
        if self._ttl_hours <= 0:
            return False
        existing = self._state.get(self._name)
        if existing is None:
            return False
        try:
            last_run = datetime.fromisoformat(existing["run_at"])
            age_hours = (datetime.now(timezone.utc) - last_run).total_seconds() / 3600
            return age_hours < self._ttl_hours
        except (KeyError, ValueError):
            return False
