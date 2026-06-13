"""Tests for the machine-equivalence drift comparator (#3059, epic #3058)."""
import importlib.util
import json
import os
from datetime import datetime, timedelta, timezone

_SPEC = importlib.util.spec_from_file_location(
    "equivalence_compare",
    os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "monitoring", "equivalence_compare.py"),
)
ec = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ec)


def _fp(role="full", **kw):
    base = {
        "role": role,
        "hostname": kw.get("hostname", role),
        "ts": kw.get("ts", "2026-06-13T12:00:00+00:00"),
        "clone_head": "abc123",
        "behind_origin": 0,
        "ahead_origin": 0,
        "harness_version": "2.1.177",
        "harness_install": "npm-global",
        "registry_sha256": "deadbeef" * 8,
        "learning_cron_ages_h": {"comprehensive-learning-nightly": 12.0, "session-analysis": 8.0},
    }
    base.update(kw)
    return base


def _codes(divs):
    return {d["code"] for d in divs}


def test_identical_boxes_no_divergence():
    divs = ec.compare([_fp("full"), _fp("contribute")])
    assert divs == []
    assert ec.worst_severity(divs) is None


def test_registry_divergence_is_critical():
    a = _fp("full")
    b = _fp("contribute", registry_sha256="cafe" * 16)
    divs = ec.compare([a, b])
    assert "registry-divergence" in _codes(divs)
    reg = next(d for d in divs if d["code"] == "registry-divergence")
    assert reg["severity"] == ec.CRITICAL
    assert ec.worst_severity(divs) == ec.CRITICAL


def test_harness_version_mismatch_is_warning():
    divs = ec.compare([_fp("full"), _fp("contribute", harness_version="2.1.99")])
    d = next(d for d in divs if d["code"] == "harness-version-mismatch")
    assert d["severity"] == ec.WARNING


def test_harness_install_mismatch_is_info():
    divs = ec.compare([_fp("full"), _fp("contribute", harness_install="native")])
    d = next(d for d in divs if d["code"] == "harness-install-mismatch")
    assert d["severity"] == ec.INFO


def test_clone_far_behind_is_warning_and_threshold_respected():
    # 14 behind -> WARNING (the real ace-linux-1 case on 2026-06-13)
    divs = ec.compare([_fp("full", behind_origin=14), _fp("contribute")])
    d = next(d for d in divs if d["code"] == "clone-behind-origin")
    assert d["severity"] == ec.WARNING
    # 3 behind -> INFO (default behind_warn=10)
    divs2 = ec.compare([_fp("full"), _fp("contribute", behind_origin=3)])
    d2 = next(d for d in divs2 if d["code"] == "clone-behind-origin")
    assert d2["severity"] == ec.INFO


def test_hub_learning_cron_stale_is_warning_only_on_full_role():
    stale = {"comprehensive-learning-nightly": 100.0, "session-analysis": 8.0}
    # stale cron on the hub (full) -> WARNING
    divs = ec.compare([_fp("full", learning_cron_ages_h=stale), _fp("contribute")])
    assert "hub-cron-stale" in _codes(divs)
    # same staleness on a non-hub (contribute) box -> NOT flagged
    divs2 = ec.compare([_fp("full"), _fp("contribute", learning_cron_ages_h=stale)])
    assert "hub-cron-stale" not in _codes(divs2)


def test_hub_learning_cron_unknown_age_is_warning():
    divs = ec.compare([_fp("full", learning_cron_ages_h={"session-analysis": 8.0}), _fp("contribute")])
    # comprehensive-learning-nightly age missing -> hub-cron-unknown
    assert "hub-cron-unknown" in _codes(divs)


def test_stale_fingerprint_detected():
    fresh = "2026-06-13T12:00:00+00:00"
    old = "2026-06-13T02:00:00+00:00"  # 10h older than fresh, default stale_h=6
    divs = ec.compare([_fp("full", ts=fresh), _fp("contribute", ts=old)])
    d = next(d for d in divs if d["code"] == "stale-fingerprint")
    assert d["severity"] == ec.WARNING
    assert "contribute" in d["boxes"]


def test_empty_input_safe():
    assert ec.compare([]) == []


def test_main_exit_codes(tmp_path):
    # one clean pair -> exit 0
    (tmp_path / "full.json").write_text(json.dumps(_fp("full")))
    (tmp_path / "contribute.json").write_text(json.dumps(_fp("contribute")))
    assert ec.main([str(tmp_path), "--json"]) == 0
    # introduce a registry divergence -> exit 2 (CRITICAL)
    (tmp_path / "contribute.json").write_text(json.dumps(_fp("contribute", registry_sha256="f00d" * 16)))
    assert ec.main([str(tmp_path)]) == 2


def test_load_dir_skips_malformed(tmp_path):
    (tmp_path / "full.json").write_text(json.dumps(_fp("full")))
    (tmp_path / "bad.json").write_text("{not json")
    fps = ec.load_dir(str(tmp_path))
    assert len(fps) == 1
