"""Aggregation and recommendation logic of scripts/fleet/collect_account_usage_fleet.py."""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FLEET = REPO / "scripts/fleet/collect_account_usage_fleet.py"
PROBE = REPO / "scripts/ai/assessment/collect-account-usage.py"

spec = importlib.util.spec_from_file_location("fleet_usage", FLEET)
fleet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fleet)

AT = dt.datetime(2026, 9, 26, 12, 0, tzinfo=dt.timezone.utc)


def cfg() -> dict:
    return {
        "accounts": {
            "claude-owner": {"provider": "claude", "holder": "owner", "fingerprint": None},
            "claude-professional": {"provider": "claude", "holder": "colleague", "fingerprint": "aaaaaaaaaaaa"},
            "codex-owner": {"provider": "codex", "holder": "owner", "fingerprint": None},
            "codex-professional": {"provider": "codex", "holder": "colleague", "fingerprint": None},
        },
        "hosts": {
            "ace-linux-1": {"claude": "claude-owner", "codex": "codex-owner"},
            "ace-linux-2": {"claude": "claude-owner"},
            "ace-win-2": {"claude": "claude-professional", "codex": "codex-professional"},
            "ace-win-1": {"claude": "claude-professional", "codex": "codex-professional"},
        },
        "policy": {"tight_headroom_pct": 10, "switch_margin_pct": 15, "max_sample_age_hours": 12},
    }


def rec(host, captured, claude=None, codex=None, reachable=True):
    r = {"host": host, "reachable": reachable, "captured_at": captured, "providers": {}}
    if claude is not None:
        r["providers"]["claude"] = {"provider": "claude", **claude}
    if codex is not None:
        r["providers"]["codex"] = {"provider": "codex", **codex}
    return r


def test_freshest_sample_per_account_and_recommendation():
    records = [
        rec("ace-linux-1", "2026-09-26T11:00:00+00:00",
            claude={"source": "oauth-api", "week_pct": 70, "five_hour_pct": 20, "fingerprint": "111111111111"},
            codex={"source": "app-server-live", "week_pct": 85, "five_hour_pct": 5, "fingerprint": "222222222222"}),
        rec("ace-linux-2", "2026-09-26T11:30:00+00:00",
            claude={"source": "oauth-api", "week_pct": 72, "five_hour_pct": 25, "fingerprint": "111111111111"}),
        rec("ace-win-2", "2026-09-26T11:20:00+00:00",
            claude={"source": "oauth-api", "week_pct": 30, "five_hour_pct": 0, "fingerprint": "aaaaaaaaaaaa"},
            codex={"source": "local-session-rate-limits", "week_pct": 40, "fingerprint": "bbbbbbbbbbbb"}),
        rec("ace-win-1", "", reachable=False),
    ]
    agg = fleet.aggregate(cfg(), records, AT)
    owner = agg["accounts"]["claude-owner"]
    assert owner["sampled_on"] == "ace-linux-2"  # freshest wins
    assert owner["week_pct"] == 72 and owner["headroom_pct"] == 28.0
    assert owner["reachable_hosts"] == ["ace-linux-1", "ace-linux-2"]
    prof = agg["accounts"]["claude-professional"]
    assert prof["headroom_pct"] == 70.0 and prof["fingerprint"] == "aaaaaaaaaaaa"
    assert agg["recommendation"]["claude"]["account"] == "claude-professional"
    assert agg["recommendation"]["claude"]["hosts"] == ["ace-win-2"]  # ace-win-1 unreachable
    assert agg["recommendation"]["claude"]["alternative"]["account"] == "claude-owner"
    assert "note" not in agg["recommendation"]["claude"]  # 70 vs 28: clear margin
    assert agg["recommendation"]["codex"]["account"] == "codex-professional"
    assert agg["hosts"]["ace-win-1"]["reachable"] is False
    assert not agg["warnings"]


def test_near_equal_accounts_carry_stay_note_and_tight_flag():
    records = [
        rec("ace-linux-1", "2026-09-26T11:00:00+00:00",
            claude={"source": "oauth-api", "week_pct": 92, "fingerprint": "111111111111"}),
        rec("ace-win-2", "2026-09-26T11:00:00+00:00",
            claude={"source": "oauth-api", "week_pct": 95, "fingerprint": "aaaaaaaaaaaa"}),
    ]
    agg = fleet.aggregate(cfg(), records, AT)
    assert agg["accounts"]["claude-owner"]["tight"] is True
    assert agg["recommendation"]["claude"]["account"] == "claude-owner"
    assert "defer marathons" in agg["recommendation"]["claude"]["note"]


def test_fingerprint_mismatch_and_stale_sample_are_excluded_with_warnings():
    records = [
        rec("ace-win-2", "2026-09-26T11:00:00+00:00",
            claude={"source": "oauth-api", "week_pct": 10, "fingerprint": "cccccccccccc"}),  # not the professional seat
        rec("ace-linux-1", "2026-09-25T20:00:00+00:00",  # 16h old
            claude={"source": "oauth-api", "week_pct": 50, "fingerprint": "111111111111"}),
    ]
    agg = fleet.aggregate(cfg(), records, AT)
    assert agg["accounts"]["claude-professional"]["source"] == "unavailable"
    assert agg["accounts"]["claude-owner"]["source"] == "unavailable"
    assert agg["recommendation"]["claude"]["account"] is None
    assert any("differs" in w for w in agg["warnings"])
    assert any("older" in w for w in agg["warnings"])


def test_unavailable_probe_is_reported_per_host_not_as_usage():
    records = [rec("ace-linux-1", "2026-09-26T11:00:00+00:00",
                   claude={"source": "unavailable", "error": "http 401"},
                   codex={"source": "app-server-live", "week_pct": 12})]
    agg = fleet.aggregate(cfg(), records, AT)
    assert agg["hosts"]["ace-linux-1"]["unavailable"] == {"claude": "http 401"}
    assert agg["accounts"]["codex-owner"]["headroom_pct"] == 88.0
    md = fleet.render_md(agg)
    assert "codex-owner" in md and "http 401" in md


def test_probe_runs_offline_and_prints_no_secrets(tmp_path):
    claude_dir = tmp_path / "claude"
    claude_dir.mkdir()
    (claude_dir / ".credentials.json").write_text(json.dumps(
        {"claudeAiOauth": {"accessToken": "sk-ant-oat-SECRET", "subscriptionType": "max", "expiresAt": 4102444800000}}))
    (claude_dir / ".claude.json").write_text(json.dumps({"oauthAccount": {"emailAddress": "someone@example.com"}}))
    codex_home = tmp_path / "codex"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text(json.dumps({"tokens": {"id_token": "x.e30.y"}}))
    proc = subprocess.run([sys.executable, str(PROBE), "--json", "--no-live", "--host", "test-1",
                           "--claude-config-dir", str(claude_dir), "--codex-home", str(codex_home)],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout
    assert "SECRET" not in out and "example.com" not in out and str(tmp_path) not in out
    data = json.loads(out)
    assert data["host"] == "test-1"
    assert data["providers"]["claude"]["fingerprint"] == fleet_fp("someone@example.com")
    assert data["providers"]["claude"]["source"] == "unavailable"
    assert data["providers"]["claude"]["tier"] == "max"
    assert data["providers"]["codex"]["source"] == "unavailable"


def fleet_fp(email: str) -> str:
    import hashlib
    return hashlib.sha256(email.lower().encode()).hexdigest()[:12]


@pytest.mark.parametrize("path", [FLEET, PROBE])
def test_scripts_compile(path):
    subprocess.run([sys.executable, "-m", "py_compile", str(path)], check=True)


def test_remote_launcher_probes_interpreter_execution_not_presence():
    # Windows Git Bash: the Microsoft Store python3 redirector stub passes
    # `command -v python3` but exits 49 "Python was not found". The launcher
    # must verify the interpreter actually executes, not that it is on PATH.
    assert 'python3 -c' in fleet.REMOTE_CMD
    assert 'command -v python3' not in fleet.REMOTE_CMD
