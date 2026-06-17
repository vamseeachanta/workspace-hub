#!/usr/bin/env python3
"""Tests for equivalence_compare.py — focus on the #3187 v2 dimensions
(off-main, stale-index-lock) plus version-awareness and role-awareness.

Run: uv run --no-project python -m pytest scripts/monitoring/tests/test_equivalence_compare.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from equivalence_compare import compare, worst_severity, CRITICAL, WARNING, INFO  # noqa: E402


def _fp(**kw):
    base = {"fingerprint_version": 2, "role": "full", "hostname": "ace-linux-1",
            "ts": "2026-06-17T12:00:00+00:00", "current_branch": "main",
            "stale_index_lock": False}
    base.update(kw)
    return base


def _codes(divs):
    return {d["code"] for d in divs}


def test_on_main_no_drift():
    divs = compare([_fp(current_branch="main")])
    assert "off-main" not in _codes(divs)
    assert "stale-index-lock" not in _codes(divs)


def test_off_main_control_plane_is_warning():
    divs = compare([_fp(role="full", current_branch="docs/handoff-x")])
    off = [d for d in divs if d["code"] == "off-main"]
    assert len(off) == 1
    assert off[0]["severity"] == WARNING


def test_off_main_contribute_is_info():
    divs = compare([_fp(role="contribute", hostname="ace-linux-2",
                        current_branch="feature/y")])
    off = [d for d in divs if d["code"] == "off-main"]
    assert len(off) == 1
    assert off[0]["severity"] == INFO


def test_stale_index_lock_is_critical_any_role():
    for role in ("full", "contribute"):
        divs = compare([_fp(role=role, stale_index_lock=True)])
        sl = [d for d in divs if d["code"] == "stale-index-lock"]
        assert len(sl) == 1, role
        assert sl[0]["severity"] == CRITICAL, role
        assert worst_severity(divs) == CRITICAL


def test_v1_fingerprint_skipped_version_aware():
    # A v1 box has no current_branch/stale_index_lock — must NOT trigger off-main
    # (prevents false positives during rollout when boxes are mixed-version).
    v1 = {"fingerprint_version": 1, "role": "full", "hostname": "old-box",
          "ts": "2026-06-17T12:00:00+00:00"}
    divs = compare([v1])
    assert "off-main" not in _codes(divs)
    assert "stale-index-lock" not in _codes(divs)


def test_mixed_version_only_v2_box_flagged():
    # v1 box (role full) lacks the v2 fields -> skipped; only the v2 box (distinct
    # role 'contribute') is flagged. Divergences key by role, matching every other check.
    v1 = {"fingerprint_version": 1, "role": "full", "hostname": "old",
          "ts": "2026-06-17T12:00:00+00:00"}
    v2_off = _fp(role="contribute", hostname="new", current_branch="wip")
    divs = compare([v1, v2_off])
    off = [d for d in divs if d["code"] == "off-main"]
    assert len(off) == 1
    assert "contribute" in off[0]["boxes"]
    assert off[0]["severity"] == INFO
