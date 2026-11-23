"""ManifestManager — atomic YAML read/update for pipeline manifest."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


class ManifestManager:
    """Read and atomically update the pipeline manifest YAML."""

    def __init__(self, manifest_path: Path) -> None:
        self._path = Path(manifest_path)

    def read(self) -> Dict[str, Any]:
        """Return manifest dict. Returns empty structure if file missing."""
        if not self._path.exists():
            return {"pipelines": {}}
        data = yaml.safe_load(self._path.read_text())
        if data is None:
            return {"pipelines": {}}
        return data

    def update(
        self,
        pipeline_name: str,
        source_url: str,
        refresh_cadence: str,
        last_run: str,
        record_count: int,
        output_path: str,
    ) -> None:
        """Update or create a pipeline entry. Atomic write via os.replace."""
        data = self.read()
        data["pipelines"][pipeline_name] = {
            "source_url": source_url,
            "refresh_cadence": refresh_cadence,
            "last_run": last_run,
            "record_count": record_count,
            "output_path": output_path,
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".yaml.tmp")
        tmp.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
        os.replace(tmp, self._path)
