# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Tests for the venue ABSENCE detector core + CLI (issue #2971, F4)."""

import argparse
import importlib.util
import sys
from pathlib import Path

import pytest

# Load the module by path (scripts/ is not a package).
_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts" / "operations" / "venue_absence_detector.py"
)
_spec = importlib.util.spec_from_file_location("venue_absence_detector", _MODULE_PATH)
vad = importlib.util.module_from_spec(_spec)
sys.modules["venue_absence_detector"] = vad
_spec.loader.exec_module(vad)


# --------------------------------------------------------------------------- #
# PURE CORE: evaluate()
# --------------------------------------------------------------------------- #


def test_healthy_returns_no_alerts():
    alerts = vad.evaluate(
        lease_present=True,
        lease_valid=True,
        mirror_ages_h=[1.0, 5.0],   # under 12h threshold
        heartbeat_age_h=2.0,        # under 12h threshold
    )
    assert alerts == []


def test_no_holder_when_lease_absent():
    alerts = vad.evaluate(
        lease_present=False,
        lease_valid=False,
        mirror_ages_h=[],
        heartbeat_age_h=None,
    )
    kinds = [a["kind"] for a in alerts]
    assert "no-holder" in kinds
    assert all(a["severity"] for a in alerts)


def test_no_holder_when_present_but_invalid():
    alerts = vad.evaluate(
        lease_present=True,
        lease_valid=False,
        mirror_ages_h=[],
        heartbeat_age_h=None,
    )
    kinds = [a["kind"] for a in alerts]
    assert kinds == ["no-holder"]


def test_stale_mirror_over_threshold():
    # threshold = 24 * 0.5 = 12h; 13h is stale.
    alerts = vad.evaluate(
        lease_present=True,
        lease_valid=True,
        mirror_ages_h=[13.0],
        heartbeat_age_h=None,
    )
    kinds = [a["kind"] for a in alerts]
    assert kinds == ["stale-mirror"]


def test_no_stale_mirror_under_threshold():
    # 11.99h is under the 12h threshold → healthy.
    alerts = vad.evaluate(
        lease_present=True,
        lease_valid=True,
        mirror_ages_h=[11.99, 0.5],
        heartbeat_age_h=None,
    )
    assert alerts == []


def test_stale_mirror_threshold_is_strict_below_sla():
    # The warn threshold (12h) must be strictly below the 24h SLA so we alert
    # with margin to act. Confirm a 12.01h mirror alerts well before 24h.
    alerts = vad.evaluate(
        lease_present=True,
        lease_valid=True,
        mirror_ages_h=[12.01],
        heartbeat_age_h=None,
    )
    assert [a["kind"] for a in alerts] == ["stale-mirror"]


def test_stale_heartbeat_over_threshold():
    alerts = vad.evaluate(
        lease_present=True,
        lease_valid=True,
        mirror_ages_h=[],
        heartbeat_age_h=18.0,
    )
    assert [a["kind"] for a in alerts] == ["stale-heartbeat"]


def test_none_heartbeat_produces_no_heartbeat_alert():
    alerts = vad.evaluate(
        lease_present=True,
        lease_valid=True,
        mirror_ages_h=[],
        heartbeat_age_h=None,
    )
    assert [a["kind"] for a in alerts if a["kind"] == "stale-heartbeat"] == []
    assert alerts == []


def test_multiple_alerts_compound():
    alerts = vad.evaluate(
        lease_present=False,
        lease_valid=False,
        mirror_ages_h=[20.0, 1.0],   # one stale, one fresh
        heartbeat_age_h=30.0,        # stale
    )
    kinds = sorted(a["kind"] for a in alerts)
    # no-holder + one stale-mirror (only the 20h) + stale-heartbeat
    assert kinds == ["no-holder", "stale-heartbeat", "stale-mirror"]


def test_custom_warn_fraction_and_sla():
    # sla=10h, warn_fraction=0.8 → threshold=8h. 9h mirror is stale.
    alerts = vad.evaluate(
        lease_present=True,
        lease_valid=True,
        mirror_ages_h=[9.0],
        heartbeat_age_h=7.0,         # under 8h → fresh
        sla_h=10.0,
        warn_fraction=0.8,
    )
    assert [a["kind"] for a in alerts] == ["stale-mirror"]


def test_evaluate_is_pure_returns_dicts_with_required_keys():
    alerts = vad.evaluate(False, False, [50.0], 50.0)
    for a in alerts:
        assert set(a.keys()) == {"kind", "detail", "severity"}


# --------------------------------------------------------------------------- #
# THIN CLI: run_cli() with injected notify_fn
# --------------------------------------------------------------------------- #


def _args(**overrides):
    base = dict(
        json=None,
        lease_present=True,
        lease_valid=True,
        mirror_age_h=[],
        heartbeat_age_h=None,
        sla_h=24.0,
        warn_fraction=0.5,
    )
    base.update(overrides)
    return argparse.Namespace(**base)


def test_cli_healthy_returns_zero_and_no_notify():
    calls = []
    rc = vad.run_cli(
        _args(lease_present=True, lease_valid=True,
              mirror_age_h=[1.0], heartbeat_age_h=2.0),
        notify_fn=calls.append,
    )
    assert rc == 0
    assert calls == []


def test_cli_calls_notify_once_per_alert_and_returns_nonzero():
    calls = []
    rc = vad.run_cli(
        _args(lease_present=False, lease_valid=False,
              mirror_age_h=[20.0], heartbeat_age_h=30.0),
        notify_fn=calls.append,
    )
    assert rc == 1
    # no-holder + stale-mirror + stale-heartbeat = 3 alerts → 3 notify calls.
    assert len(calls) == 3
    assert {c["kind"] for c in calls} == {
        "no-holder", "stale-mirror", "stale-heartbeat",
    }


def test_cli_single_alert_fires_one_notify():
    calls = []
    rc = vad.run_cli(
        _args(lease_present=False, lease_valid=False),
        notify_fn=calls.append,
    )
    assert rc == 1
    assert len(calls) == 1
    assert calls[0]["kind"] == "no-holder"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
