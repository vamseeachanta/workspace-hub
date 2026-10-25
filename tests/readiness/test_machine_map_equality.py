"""Public projection and hand-calculated freshness contracts for issue #3498."""
import importlib.util
import json
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("map_equality", ROOT / "scripts/readiness/build-equality-matrix.py")
bem = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bem)


def pointer():
    return {"present": True, "updated_at": "2026-10-01T00:00:00+00:00", "content_hash": "a" * 64}


@pytest.mark.parametrize("limit,want", [(86400, "MAP-FRESH"), (86399, "MAP-STALE"),
                                        (None, "NOT_EVALUATED"), (True, "NOT_EVALUATED"),
                                        (float("inf"), "NOT_EVALUATED"), (-1, "NOT_EVALUATED")])
def test_age_limit_is_required_and_boundary_is_inclusive(limit, want):
    """Hand calculation: Oct 2 midnight minus Oct 1 midnight = 24*60*60 seconds.

    The limit is synthetic test input; issue #3498 specifies no policy limit.
    """
    now = datetime(2026, 10, 2, tzinfo=UTC)
    assert bem.machine_map_verdict({"machine_map": pointer()}, limit, now) == want


@pytest.mark.parametrize("change", [
    {"present": "true"}, {"present": False}, {"content_hash": "private-detail"},
    {"updated_at": "2026-10-01"}, {"updated_at": "2026-10-03T00:00:00+00:00"},
    {"extra": "private-detail"},
])
def test_invalid_pointer_is_missing_evidence(change):
    p = pointer() | change
    assert bem.machine_map_verdict({"machine_map": p}, 86400,
                                  datetime(2026, 10, 2, tzinfo=UTC)) == "MISSING-EVIDENCE"


@pytest.mark.parametrize("offset", ["+00:60", "+01:99", "-00:60", "-01:99", "+24:00", "-24:00"])
def test_public_verdict_rejects_invalid_timezone_offset(offset):
    p = pointer() | {"updated_at": "2026-10-01T00:00:00" + offset}
    assert bem.machine_map_verdict({"machine_map": p}, 86400,
                                  datetime(2026, 10, 2, tzinfo=UTC)) == "MISSING-EVIDENCE"


@pytest.mark.parametrize("offset", ["Z", "+00:00", "-00:00", "+23:59", "-23:59"])
def test_public_verdict_accepts_valid_timezone_offset(offset):
    # At Oct 2 midnight these observations are between 60 and 172740 seconds old.
    p = pointer() | {"updated_at": "2026-10-01T00:00:00" + offset}
    assert bem.machine_map_verdict({"machine_map": p}, 172740,
                                  datetime(2026, 10, 2, tzinfo=UTC)) == "MAP-FRESH"


def test_map_row_is_registered_and_not_compared_to_peers():
    assert "machine_map" in bem.DISPLAY_DIMS
    assert sum(dims.count("machine_map") for _, _, dims in bem.GROUPS) == 1
    report = {"machine_map": pointer(), "dimensions": {}, "provenance": {
        "dirty": False, "behind_main": 0, "ahead_main": 0, "origin_ref_age_h": 0}}
    assert bem.verdict_for("machine_map", "compute", {"compute": report}, {},
                           {"compute": {"status": "active"}}, []) == "NOT_EVALUATED"


def test_collector_emits_only_pointer_fields(tmp_path):
    """Run only against an empty synthetic workspace: no solver helper is present."""
    ws = tmp_path / "public"
    ws.mkdir()
    scripts = ws / "scripts/readiness"
    scripts.mkdir(parents=True)
    for name in ("collect-equality.sh", "machine_map.py"):
        shutil.copyfile(ROOT / "scripts/readiness" / name, scripts / name)
    admin = tmp_path / "private"
    maps = admin / "machine-ecosystem/machines"
    maps.mkdir(parents=True)
    (admin / "machine-ecosystem/private.json").write_text('{"visibility":"private"}', encoding="utf-8", newline="\n")
    report = {"schema_version": 1, "machine": "compute", "role": "executor",
              "source": "seeded-manual", "updated_at": pointer()["updated_at"],
              "data_sources": [{"name": "private-source", "reachable": True}],
              "services": [], "auth_surfaces": {"gh": False}}
    (maps / "compute.yaml").write_text(json.dumps(report), encoding="utf-8", newline="\n")
    result = subprocess.run(["bash", str(scripts / "collect-equality.sh"),
                             "--stdout", "--machine", "compute"],
                            env={**os.environ, "WORKSPACE_HUB": str(ws),
                                 "MACHINE_MAP_ADMIN_ROOT": str(admin)},
                            capture_output=True, text=True, check=True)
    public = yaml.safe_load(result.stdout)["machine_map"]
    assert public["present"] is True
    assert set(public) == {"present", "updated_at", "content_hash"}
    assert "private-source" not in result.stdout and str(admin) not in result.stdout
