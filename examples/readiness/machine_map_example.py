#!/usr/bin/env python3
"""Synthetic worked example; writes only to an explicit external directory.

Expected answers are hand-derived in docs/readiness/machine-map.md. Example dates
are synthetic inputs, not observations of operational systems.
"""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("machine_map", ROOT / "scripts/readiness/machine_map.py")
mm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm)


def run(output):
    output = output.resolve()
    if output == ROOT or output.is_relative_to(ROOT) or ROOT.is_relative_to(output):
        raise ValueError("example output must be outside the public checkout")
    area = output / "machine-ecosystem"
    area.mkdir(parents=True, exist_ok=True)
    marker = area / "private.json"
    if not marker.exists():
        marker.write_text('{"visibility":"private"}\n')
    data = output / "synthetic-data"
    data.mkdir(exist_ok=True)
    config = {"role": "executor", "probe_timeout_seconds": 1,
              "data_sources": [{"name": "archive", "path": str(data)},
                               {"name": "missing", "path": str(data / "absent")}],
              "services": [], "auth_surfaces": []}
    value = mm.collect("compute", config, "2026-10-01T00:00:00+00:00")
    assert value["data_sources"] == [{"name": "archive", "reachable": True},
                                     {"name": "missing", "reachable": False}]
    mm.write_map(output, value)
    seed = {**value, "machine": "portable", "role": "portable", "source": "seeded-manual",
            "data_sources": [], "services": []}
    mm.write_map(output, seed)
    assert not mm.write_map(output, value)
    html = mm.build_matrix(output, ["compute", "portable", "producer"])
    assert "MISSING-EVIDENCE" in html and "seeded-manual" in html
    mm.atomic_write(mm.safe_target(mm.private_area(output), Path("matrix.html")), html.encode())
    return mm.project(output, "compute")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    print(json.dumps(run(parser.parse_args().output_dir), sort_keys=True))
