#!/usr/bin/env python3
"""TDD tests for reconcile.py board-size report + card_count recompute (#2878 P0).

Two related capabilities the kanban reorg needs:
  * a size report flagging boards over the ≤30 policy (the taxonomy must stay
    right-sized; "≤30" was policy-only, never mechanism) — pure, no IO
  * card_count drift detection + an on-demand recompute (manifest card_count is a
    frozen integer that drifts: nothing consumes it and reconcile never updated
    it). Per feedback_doc_counter_rule_writetime, a counter is a write-time
    recompute, not a stored integer.

Pure functions are tested with dict fixtures; update_manifest_counts is tested
against a tmp manifest+boards tree. Hermetic — no gh, no live kanban.

Run: uv run --with ruamel.yaml pytest tests/test_reconcile_size_report.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RECONCILE_PY = REPO_ROOT / "scripts" / "kanban" / "reconcile.py"


def _import_reconcile():
    spec = importlib.util.spec_from_file_location("kanban_reconcile", RECONCILE_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kanban_reconcile"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def rc():
    return _import_reconcile()


def _board(slug, n_issue, *, n_gap=0):
    cards = [{"idempotency_key": f"gh:r#{i}", "source": "github_issue"} for i in range(n_issue)]
    cards += [{"idempotency_key": f"gap:{i}", "source": "detected_gap"} for i in range(n_gap)]
    return {"board": {"slug": slug}, "cards": cards}


def test_count_issue_cards_counts_only_github_issue(rc):
    b = _board("x", 5, n_gap=3)
    assert rc.count_issue_cards(b) == 5  # detected_gap not counted


def test_count_issue_cards_handles_empty(rc):
    assert rc.count_issue_cards({"board": {"slug": "x"}}) == 0
    assert rc.count_issue_cards({"board": {"slug": "x"}, "cards": None}) == 0


def test_size_report_flags_over_limit_only(rc):
    rebuilt = {
        Path("a.yaml"): _board("big", 131),
        Path("b.yaml"): _board("ok", 30),       # exactly at limit -> not flagged
        Path("c.yaml"): _board("mid", 45),
    }
    rows = rc.board_size_report(rebuilt, limit=30)
    assert rows == [("big", 131), ("mid", 45)], rows  # sorted desc, 'ok' excluded


def test_size_report_respects_custom_limit(rc):
    rebuilt = {Path("a.yaml"): _board("s", 25)}
    assert rc.board_size_report(rebuilt, limit=20) == [("s", 25)]
    assert rc.board_size_report(rebuilt, limit=30) == []


def test_card_count_drift_detects_mismatch(rc):
    rebuilt = {
        Path("/k/boards/x.yaml"): _board("x", 96),
        Path("/k/boards/y.yaml"): _board("y", 10),
    }
    entries = [
        rc.BoardEntry(slug="x", tier="domain", repo="r", domain="x",
                      file=Path("/k/boards/x.yaml"), card_count=93),   # stale
        rc.BoardEntry(slug="y", tier="domain", repo="r", domain="y",
                      file=Path("/k/boards/y.yaml"), card_count=10),   # correct
    ]
    drift = rc.card_count_drift(rebuilt, entries)
    assert drift == [("x", 93, 96)], drift  # only the stale board reported


def test_update_manifest_counts_rewrites_to_actual(rc, tmp_path):
    kanban = tmp_path
    boards = kanban / "boards"
    boards.mkdir()
    (boards / "repo-x.yaml").write_text(
        "board:\n  slug: repo-x\ncards:\n"
        "  - idempotency_key: gh:r#1\n    source: github_issue\n"
        "  - idempotency_key: gh:r#2\n    source: github_issue\n",
        encoding="utf-8",
    )
    (kanban / "manifest.yaml").write_text(
        "manifest:\n  boards:\n"
        "    - slug: repo-x\n      tier: repo\n      repo: r\n      domain: null\n"
        "      file: boards/repo-x.yaml\n      card_count: 99\n",
        encoding="utf-8",
    )
    changed = rc.update_manifest_counts(kanban)
    assert changed is True
    text = (kanban / "manifest.yaml").read_text(encoding="utf-8")
    assert "card_count: 2" in text, text
    assert "card_count: 99" not in text
    # idempotent: a second run makes no change
    assert rc.update_manifest_counts(kanban) is False


# ── adversarial-review regressions ───────────────────────────────────────────

@pytest.mark.parametrize("value,expected", [(5, 5), ("7", 7), (None, 0), ("tbd", 0), ("", 0)])
def test_coerce_int_is_tolerant(rc, value, expected):
    # MAJOR: a non-numeric manifest card_count must NEVER crash the reconcile
    # (load_manifest_entries runs at the top of every */20 cron run).
    assert rc._coerce_int(value) == expected


def test_non_numeric_card_count_does_not_crash_manifest_load(rc, tmp_path):
    kanban = tmp_path
    (kanban / "boards").mkdir()
    (kanban / "boards" / "repo-x.yaml").write_text(
        "board:\n  slug: repo-x\ncards: []\n", encoding="utf-8")
    (kanban / "manifest.yaml").write_text(
        "manifest:\n  boards:\n"
        "    - slug: repo-x\n      tier: repo\n      repo: r\n      domain: null\n"
        "      file: boards/repo-x.yaml\n      card_count: tbd\n",
        encoding="utf-8",
    )
    entries = rc.load_manifest_entries(kanban)  # must not raise
    assert entries[0].card_count == 0
    # update_manifest_counts heals the bad value to the real count (0 here).
    assert rc.update_manifest_counts(kanban) is False  # already 0 actual


def test_update_manifest_counts_heals_non_numeric(rc, tmp_path):
    kanban = tmp_path
    (kanban / "boards").mkdir()
    (kanban / "boards" / "repo-x.yaml").write_text(
        "board:\n  slug: repo-x\ncards:\n"
        "  - idempotency_key: gh:r#1\n    source: github_issue\n",
        encoding="utf-8",
    )
    (kanban / "manifest.yaml").write_text(
        "manifest:\n  boards:\n"
        "    - slug: repo-x\n      tier: repo\n      repo: r\n"
        "      file: boards/repo-x.yaml\n      card_count: tbd\n",
        encoding="utf-8",
    )
    assert rc.update_manifest_counts(kanban) is True
    assert "card_count: 1" in (kanban / "manifest.yaml").read_text(encoding="utf-8")
