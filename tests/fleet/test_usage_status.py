"""Seat status regressions; every provider and transport operation is stubbed."""
import datetime as dt
import importlib.util
import json
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fleet = load("status_fleet", "scripts/fleet/collect_account_usage_fleet.py")
probe = load("status_probe", "scripts/ai/assessment/collect-account-usage.py")
STAMP = "2026-10-29T09:16:00+00:00"
AT = dt.datetime.fromisoformat(STAMP)
CONFIG = {"accounts": {"seat": {"provider": "claude"}},
          "hosts": {"solver-workstation": {"claude": "seat"}}}


@pytest.mark.parametrize("provider,reachable,status", [
    ({"source": "oauth-api", "week_pct": 0}, True, "ok"),
    ({"source": "unavailable", "token_expired": True}, True, "auth-expired"),
    ({"source": "unavailable", "error": "http 401"}, True, "auth-expired"),
    ({"source": "unavailable", "error": "OAuth session expired and could not be refreshed"}, True, "auth-expired"),
    ({"source": "unavailable", "status": "unreachable"}, True, "unreachable"),
    ({}, True, "not-reported"),
    ({}, False, "unreachable"),
])
def test_seat_status(provider, reachable, status):
    records = [{"host": "solver-workstation", "reachable": reachable,
                "captured_at": STAMP, "probed_at": STAMP,
                "providers": {"claude": provider}}]
    agg = fleet.aggregate(CONFIG, records, AT)
    row = agg["accounts"]["seat"]
    assert row["status"] == status
    assert row["probed_at"] == STAMP
    assert agg["hosts"]["solver-workstation"]["providers"]["claude"]["status"] == status
    assert status in fleet.render_md(agg)
    if status != "ok":
        assert row.get("week_pct") is None
        assert agg["recommendation"]["claude"]["account"] is None


def test_missing_record_is_not_reported():
    row = fleet.aggregate(CONFIG, [], AT)["accounts"]["seat"]
    assert row["status"] == "not-reported"
    assert row["probed_at"] is None


@pytest.mark.parametrize("failure,status", [(401, "auth-expired"), (503, "unreachable"),
                                            ("timeout", "unreachable")])
def test_provider_failure_status(tmp_path, monkeypatch, failure, status):
    monkeypatch.setattr(probe, "claude_identity", lambda _: (None, {}))
    monkeypatch.setattr(probe, "read_json", lambda _: {"claudeAiOauth": {"accessToken": "stub"}})
    def fail(*args, **kwargs):
        if isinstance(failure, int):
            raise urllib.error.HTTPError("", failure, "stub", {}, None)
        raise TimeoutError()
    monkeypatch.setattr(probe.urllib.request, "urlopen", fail)
    row = probe.probe_claude(tmp_path, 1, True)
    assert row["status"] == status
    assert dt.datetime.fromisoformat(row["probed_at"])


def test_expired_token_is_reported_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(probe, "claude_identity", lambda _: (None, {}))
    monkeypatch.setattr(probe, "read_json", lambda _: {"claudeAiOauth": {"accessToken": "stub", "expiresAt": 1}})
    monkeypatch.setattr(probe.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network called"))
    assert probe.probe_claude(tmp_path, 1, True)["status"] == "auth-expired"


def test_all_unreachable_is_published(tmp_path, monkeypatch):
    monkeypatch.setattr(fleet, "load_config", lambda _: CONFIG)
    monkeypatch.setattr(fleet.fsl, "load_map", lambda _: {})
    monkeypatch.setattr(fleet, "assert_publishable", lambda *a: None)
    monkeypatch.setattr(fleet, "run_probe", lambda *a: {
        "host": "solver-workstation", "reachable": False, "probed_at": STAMP})
    out, md = tmp_path / "usage.json", tmp_path / "usage.md"
    assert fleet.main(["--out", str(out), "--md", str(md)]) == 0
    assert json.loads(out.read_text())["accounts"]["seat"]["status"] == "unreachable"


def test_valid_peer_and_failed_peer_both_remain_visible():
    config = {"accounts": {"seat": {"provider": "claude"}},
              "hosts": {"build-worker": {"claude": "seat"},
                        "solver-workstation": {"claude": "seat"}}}
    records = [
        {"host": "build-worker", "reachable": True, "captured_at": STAMP,
         "providers": {"claude": {"source": "oauth-api", "week_pct": 25}}},
        {"host": "solver-workstation", "reachable": True, "captured_at": STAMP,
         "providers": {"claude": {"source": "unavailable", "token_expired": True}}},
    ]
    agg = fleet.aggregate(config, records, AT)
    assert agg["accounts"]["seat"]["status"] == "ok"
    assert agg["accounts"]["seat"]["week_pct"] == 25
    assert agg["hosts"]["solver-workstation"]["providers"]["claude"]["status"] == "auth-expired"


@pytest.mark.parametrize("kind", ["old", "mismatched", "reset", "missing-time"])
def test_unqualified_sample_is_not_ok(kind):
    import copy
    config = copy.deepcopy(CONFIG)
    provider = {"source": "oauth-api", "week_pct": 25}
    record = {"host": "solver-workstation", "reachable": True,
              "captured_at": STAMP, "providers": {"claude": provider}}
    if kind == "old":
        record["captured_at"] = "2026-10-27T00:00:00+00:00"
    elif kind == "mismatched":
        config["accounts"]["seat"]["fingerprint"] = "expected"
        provider["fingerprint"] = "different"
    elif kind == "reset":
        provider["week_resets_at"] = "2026-10-28T00:00:00+00:00"
    else:
        record.pop("captured_at")
    agg = fleet.aggregate(config, [record], AT)
    assert agg["accounts"]["seat"]["status"] == "not-reported"
    assert agg["recommendation"]["claude"]["account"] is None


@pytest.mark.parametrize("output", [b"{}", b"unparseable", b"[]"])
def test_transport_probes_are_stubbed_and_timestamped(monkeypatch, output):
    import subprocess
    monkeypatch.setattr(fleet.subprocess, "run", lambda *a, **k:
                        subprocess.CompletedProcess([], 0, output, b""))
    row = fleet.run_probe("solver-workstation", {"local": True}, 1, b"")
    assert dt.datetime.fromisoformat(row["probed_at"])


def test_transport_timeout_is_timestamped(monkeypatch):
    import subprocess
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("stub", 1)
    monkeypatch.setattr(fleet.subprocess, "run", timeout)
    row = fleet.run_probe("solver-workstation", {"local": True}, 1, b"")
    assert row["reachable"] is False
    assert row["note"] == "timeout"
    assert dt.datetime.fromisoformat(row["probed_at"])
