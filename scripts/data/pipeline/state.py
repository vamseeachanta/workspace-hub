"""Pipeline state — JSON-based incremental tracking per pipeline.

Modeled on worldenergydata EIAIngestionState pattern.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class PipelineState:
    """Track last-run state per pipeline for incremental processing."""

    def __init__(self, state_dir: Path) -> None:
        self._state_dir = Path(state_dir)

    def get(self, pipeline_name: str) -> Optional[Dict[str, Any]]:
        """Return state dict for pipeline, or None if never run."""
        fp = self._state_dir / f"{pipeline_name}.json"
        if not fp.exists():
            return None
        return json.loads(fp.read_text())

    def save(
        self,
        pipeline_name: str,
        last_value: str,
        record_count: int,
        run_at: str,
    ) -> None:
        """Persist state for a pipeline run."""
        self._state_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "pipeline_name": pipeline_name,
            "last_value": last_value,
            "record_count": record_count,
            "run_at": run_at,
        }
        fp = self._state_dir / f"{pipeline_name}.json"
        fp.write_text(json.dumps(data, indent=2) + "\n")
