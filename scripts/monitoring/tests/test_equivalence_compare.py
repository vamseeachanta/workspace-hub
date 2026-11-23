"""Tests for equivalence_compare.py checks 7 (primary-off-main) and 8 (stale-index-lock).

Added for #3187: the sentinel must detect when dev-primary (role=full) parks off
`main`, and when a stale .git/index.lock is reported, so the install-doctor repair
arm (#3184) can act on the drift.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from equivalence_compare import compare, WARNING  # noqa: E402


def _fp(**kw):
    base = {"role": "full", "hostname": "ace-linux-1", "ts": "2026-06-17T10:00:00+00:00"}
    base.update(kw)
    return base


def _codes(divs):
    return {d["code"] for d in divs}


def test_compare_primary_off_main_warning():
    divs = compare([_fp(on_main=False)])
    assert "primary-off-main" in _codes(divs)
    d = next(d for d in divs if d["code"] == "primary-off-main")
    assert d["severity"] == WARNING


def test_compare_primary_on_main_no_warn():
    divs = compare([_fp(on_main=True)])
    assert "primary-off-main" not in _codes(divs)


def test_compare_contribute_off_main_no_warn():
    # off-main on a non-full role is normal (secondary boxes aren't the cron hub).
    divs = compare([_fp(role="contribute", hostname="ace-linux-2", on_main=False)])
    assert "primary-off-main" not in _codes(divs)


def test_compare_stale_lock_warning():
    divs = compare([_fp(index_lock_stale_min=8)])
    assert "stale-index-lock" in _codes(divs)
    d = next(d for d in divs if d["code"] == "stale-index-lock")
    assert d["severity"] == WARNING


def test_compare_no_stale_lock_when_null():
    divs = compare([_fp(index_lock_stale_min=None)])
    assert "stale-index-lock" not in _codes(divs)


def test_compare_missing_new_fields_is_silent():
    # Old fingerprints (pre-#3187) lack both fields entirely -> no new divergences.
    divs = compare([_fp()])
    assert "primary-off-main" not in _codes(divs)
    assert "stale-index-lock" not in _codes(divs)
