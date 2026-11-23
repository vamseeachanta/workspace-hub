"""TDD tests for WRK-1020: update_portfolio_signals.py + update-portfolio-signals.sh"""
import hashlib
import json
import shutil
import subprocess
import sys
import textwrap
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Locate repo root and add scripts/cron to path
REPO_ROOT = Path(__file__).parents[2]
SCRIPT_DIR = REPO_ROOT / "scripts" / "cron"
WRAPPER_SH = SCRIPT_DIR / "update-portfolio-signals.sh"
ENTRYPOINT = SCRIPT_DIR / "update_portfolio_signals.py"

sys.path.insert(0, str(SCRIPT_DIR))
import update_portfolio_signals as ups  # noqa: E402


# ── helpers ──────────────────────────────────────────────────────────────────

def make_archive_file(tmp_path, name, orchestrator, category, completed_at, extra=""):
    p = tmp_path / name
    p.write_text(
        f"---\nid: {name}\norchestrator: {orchestrator}\n"
        f"category: {category}\ncompleted_at: {completed_at}\n{extra}---\nbody\n"
    )
    return p


def today_str(offset=0):
    return (date.today() - timedelta(days=offset)).strftime("%Y-%m-%dT00:00:00Z")


# ── AC-1: script existence + uv enforcement ───────────────────────────────────

def test_script_exists_and_uses_uv_no_project_python():
    assert WRAPPER_SH.exists(), "update-portfolio-signals.sh missing"
    text = WRAPPER_SH.read_text()
    assert "uv run --no-project python" in text


def test_python_entrypoint_exists():
    assert ENTRYPOINT.exists(), "update_portfolio_signals.py missing"


def test_atomic_write_replaces_file(tmp_path):
    out = tmp_path / "signals.yaml"
    out.write_text("old: content\n")
    counts = {"claude": {"harness": 1, "engineering": 0, "data": 0, "other": 0},
              "codex": {"harness": 0, "engineering": 0, "data": 0, "other": 0},
              "gemini": {"harness": 0, "engineering": 0, "data": 0, "other": 0}}
    l2_meta = {"files_scanned": 1, "files_with_orchestrator": 1,
               "files_skipped_no_orchestrator": 0, "files_skipped_malformed": 0}
    ups.write_output(out, counts, [], {}, l2_meta, dry_run=False)
    assert out.exists()
    assert not (tmp_path / "signals.yaml.tmp").exists()
    data = yaml.safe_load(out.read_text())
    assert data["provider_activity"]["claude"]["harness"] == 1


def test_state_directory_created_if_missing(tmp_path):
    nested = tmp_path / "deep" / "state" / "signals.yaml"
    counts = {p: {"harness": 0, "engineering": 0, "data": 0, "other": 0}
              for p in ("claude", "codex", "gemini")}
    l2_meta = {"files_scanned": 0, "files_with_orchestrator": 0,
               "files_skipped_no_orchestrator": 0, "files_skipped_malformed": 0}
    ups.write_output(nested, counts, [], {}, l2_meta, dry_run=False)
    assert nested.exists()


# ── AC-2: L2 provider activity counts ────────────────────────────────────────

def test_provider_activity_counts_from_completed_at(tmp_path):
    make_archive_file(tmp_path, "a.md", "claude", "harness", today_str(1))
    make_archive_file(tmp_path, "b.md", "codex", "engineering", today_str(5))
    counts, meta = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert counts["claude"]["harness"] == 1
    assert counts["codex"]["engineering"] == 1
    assert meta["files_scanned"] == 2


def test_completed_at_window_boundary_inclusive(tmp_path):
    make_archive_file(tmp_path, "edge.md", "claude", "harness", today_str(30))
    make_archive_file(tmp_path, "out.md", "claude", "harness", today_str(31))
    counts, _ = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert counts["claude"]["harness"] == 1


def test_missing_orchestrator_field_skipped(tmp_path):
    p = tmp_path / "no_orch.md"
    p.write_text(f"---\nid: x\ncategory: harness\ncompleted_at: {today_str(1)}\n---\nbody\n")
    counts, meta = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert sum(counts[p][c] for p in counts for c in counts[p]) == 0
    assert meta["files_skipped_no_orchestrator"] == 1


def test_unknown_orchestrator_skipped_and_logged(tmp_path):
    make_archive_file(tmp_path, "unk.md", "gpt4", "harness", today_str(1))
    counts, meta = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert sum(counts[p][c] for p in counts for c in counts[p]) == 0
    assert meta["files_skipped_no_orchestrator"] == 1


def test_missing_category_field_to_other(tmp_path):
    p = tmp_path / "no_cat.md"
    p.write_text(f"---\nid: x\norchestrator: claude\ncompleted_at: {today_str(1)}\n---\n")
    counts, _ = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert counts["claude"]["other"] == 1


def test_other_bucket_categories(tmp_path):
    for i, cat in enumerate(["platform", "maintenance", "business", "personal", "uncategorised"]):
        make_archive_file(tmp_path, f"f{i}.md", "claude", cat, today_str(i + 1))
    counts, _ = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert counts["claude"]["other"] == 5


def test_malformed_frontmatter_skipped_with_meta(tmp_path):
    p = tmp_path / "bad.md"
    p.write_text("---\n: broken: yaml: [\n---\nbody\n")
    counts, meta = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert meta["files_skipped_malformed"] == 1
    assert sum(counts[pr][c] for pr in counts for c in counts[pr]) == 0


def test_bad_completed_at_skipped_with_meta(tmp_path):
    make_archive_file(tmp_path, "bad_date.md", "claude", "harness", "not-a-date")
    counts, meta = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert meta["files_skipped_malformed"] == 1


def test_recursive_archive_glob(tmp_path):
    sub = tmp_path / "2026-03"
    sub.mkdir()
    make_archive_file(tmp_path, "root.md", "claude", "harness", today_str(1))
    make_archive_file(sub, "nested.md", "codex", "engineering", today_str(2))
    counts, meta = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert meta["files_scanned"] == 2
    assert counts["claude"]["harness"] == 1
    assert counts["codex"]["engineering"] == 1


def test_l2_meta_provenance_written(tmp_path):
    make_archive_file(tmp_path, "a.md", "claude", "harness", today_str(1))
    _, meta = ups.collect_l2_counts(tmp_path, lookback_days=30)
    for key in ("files_scanned", "files_with_orchestrator",
                "files_skipped_no_orchestrator", "files_skipped_malformed"):
        assert key in meta


def test_nonzero_skip_meta_prevents_silent_all_zero(tmp_path):
    p = tmp_path / "no_orch.md"
    p.write_text(f"---\nid: x\ncategory: harness\ncompleted_at: {today_str(1)}\n---\n")
    counts, meta = ups.collect_l2_counts(tmp_path, lookback_days=30)
    total = sum(counts[pr][c] for pr in counts for c in counts[pr])
    assert total == 0
    assert meta["files_skipped_no_orchestrator"] > 0


# ── AC-4 / AC-4b: --dry-run + --lookback ─────────────────────────────────────

def test_dry_run_no_write(tmp_path, capsys):
    out = tmp_path / "signals.yaml"
    counts = {p: {"harness": 0, "engineering": 0, "data": 0, "other": 0}
              for p in ("claude", "codex", "gemini")}
    l2_meta = {"files_scanned": 0, "files_with_orchestrator": 0,
               "files_skipped_no_orchestrator": 0, "files_skipped_malformed": 0}
    ups.write_output(out, counts, [], {}, l2_meta, dry_run=True)
    assert not out.exists()
    captured = capsys.readouterr()
    assert "provider_activity" in captured.out


def test_lookback_flag_changes_counts(tmp_path):
    make_archive_file(tmp_path, "recent.md", "claude", "harness", today_str(5))
    make_archive_file(tmp_path, "old.md", "claude", "engineering", today_str(25))
    counts7, _ = ups.collect_l2_counts(tmp_path, lookback_days=7)
    counts30, _ = ups.collect_l2_counts(tmp_path, lookback_days=30)
    assert counts7["claude"]["engineering"] == 0
    assert counts30["claude"]["engineering"] == 1


def test_lookback_flag_rejects_invalid_values():
    for bad in ("0", "-1", "abc", "1.5"):
        with pytest.raises((ValueError, SystemExit)):
            ups.validate_lookback(bad)


# ── AC-3: L3 gemini capability research ──────────────────────────────────────

def test_gemini_query_skipped_when_cli_missing(tmp_path):
    with patch("shutil.which", return_value=None):
        signals, meta = ups.run_l3_query("engineering", prior_signals=[], timeout=60)
    assert signals == []
    assert meta["carry_forward"] is True
    assert meta["query_attempted"] is False


def test_carry_forward_on_cli_failure(tmp_path):
    prior = [{"date": today_str(1), "provider": "claude",
              "capability": "test", "impact": "low",
              "source": "https://anthropic.com/blog/test"}]
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    with patch("shutil.which", return_value="/usr/bin/gemini"), \
         patch("subprocess.run", return_value=mock_result):
        signals, meta = ups.run_l3_query("engineering", prior_signals=prior, timeout=60)
    assert signals == prior
    assert meta["carry_forward"] is True


def test_carry_forward_on_json_parse_failure(tmp_path):
    prior = [{"date": today_str(1), "provider": "claude",
              "capability": "x", "impact": "low",
              "source": "https://anthropic.com/blog/x"}]
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "not valid json at all {{{["
    with patch("shutil.which", return_value="/usr/bin/gemini"), \
         patch("subprocess.run", return_value=mock_result):
        signals, meta = ups.run_l3_query("engineering", prior_signals=prior, timeout=60)
    assert signals == prior
    assert meta["carry_forward"] is True
    assert meta["parse_success"] is False


def test_carry_forward_on_all_invalid_items(tmp_path):
    prior = [{"date": today_str(1), "provider": "claude",
              "capability": "x", "impact": "low",
              "source": "https://anthropic.com/blog/x"}]
    # All items have unofficial sources → filtered to zero → carry forward
    bad_signals = json.dumps([
        {"date": today_str(1), "provider": "claude",
         "capability": "test", "impact": "high",
         "source": "https://unofficial.io/blog"}
    ])
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = bad_signals
    with patch("shutil.which", return_value="/usr/bin/gemini"), \
         patch("subprocess.run", return_value=mock_result):
        signals, meta = ups.run_l3_query("engineering", prior_signals=prior, timeout=60)
    assert signals == prior
    assert meta["carry_forward"] is True


def test_structured_prompt_json_parsed_and_validated():
    raw = [{"date": today_str(1), "provider": "claude",
            "capability": "tool use", "impact": "high",
            "source": "https://anthropic.com/blog/tool-use",
            "engineering_domains": ["subsea"]}]
    result = ups.filter_official_sources(raw)
    assert len(result) == 1


def test_non_official_sources_rejected():
    signals = [
        {"date": today_str(1), "provider": "claude",
         "capability": "ok", "impact": "high",
         "source": "https://anthropic.com/blog/ok"},
        {"date": today_str(1), "provider": "claude",
         "capability": "bad", "impact": "high",
         "source": "https://unofficial.io/bad"},
    ]
    result = ups.filter_official_sources(signals)
    assert len(result) == 1
    assert result[0]["capability"] == "ok"


def test_signal_retention_prunes_older_than_30_days():
    old = {"date": (date.today() - timedelta(days=31)).strftime("%Y-%m-%dT00:00:00Z"),
           "provider": "claude", "capability": "stale", "impact": "low",
           "source": "https://anthropic.com/blog/stale"}
    fresh = {"date": today_str(5), "provider": "claude",
             "capability": "fresh", "impact": "high",
             "source": "https://anthropic.com/blog/fresh"}
    result = ups.prune_signals([old, fresh], days=30)
    assert len(result) == 1
    assert result[0]["capability"] == "fresh"


def test_idempotent_no_duplicate_signals_same_day():
    sig = {"date": today_str(1), "provider": "claude",
           "capability": "dup", "impact": "low",
           "source": "https://anthropic.com/blog/dup"}
    result = ups.dedup_signals([sig], [sig])
    assert len(result) == 1


def test_signal_cap_limits_to_five_new_and_twenty_total():
    existing = [
        {"date": today_str(i + 2), "provider": "claude",
         "capability": f"old-{i}", "impact": "low",
         "source": "https://anthropic.com/blog/old"}
        for i in range(18)
    ]
    new_signals = [
        {"date": today_str(1), "provider": "claude",
         "capability": f"new-{i}", "impact": "high",
         "source": "https://anthropic.com/blog/new"}
        for i in range(8)
    ]
    result = ups.merge_signals(existing, new_signals, max_new=5, max_total=20)
    assert len(result) <= 20
    new_caps = [s["capability"] for s in result if s["capability"].startswith("new-")]
    assert len(new_caps) <= 5


def test_mode_selection_engineering_vs_general():
    counts_eng = {"claude": {"harness": 1, "engineering": 5, "data": 0, "other": 0},
                  "codex": {"harness": 0, "engineering": 0, "data": 0, "other": 0},
                  "gemini": {"harness": 0, "engineering": 0, "data": 0, "other": 0}}
    assert ups.select_l3_mode(counts_eng) == "engineering"

    counts_gen = {"claude": {"harness": 5, "engineering": 1, "data": 0, "other": 0},
                  "codex": {"harness": 0, "engineering": 0, "data": 0, "other": 0},
                  "gemini": {"harness": 0, "engineering": 0, "data": 0, "other": 0}}
    assert ups.select_l3_mode(counts_gen) == "general"


def test_mode_selection_tie_goes_engineering():
    counts = {"claude": {"harness": 3, "engineering": 3, "data": 0, "other": 0},
              "codex": {"harness": 0, "engineering": 0, "data": 0, "other": 0},
              "gemini": {"harness": 0, "engineering": 0, "data": 0, "other": 0}}
    assert ups.select_l3_mode(counts) == "engineering"


def test_l3_meta_written(tmp_path):
    out = tmp_path / "signals.yaml"
    counts = {p: {"harness": 0, "engineering": 0, "data": 0, "other": 0}
              for p in ("claude", "codex", "gemini")}
    l2_meta = {"files_scanned": 0, "files_with_orchestrator": 0,
               "files_skipped_no_orchestrator": 0, "files_skipped_malformed": 0}
    l3_meta = {"query_attempted": False, "query_mode": "general", "parse_success": False,
               "signals_added": 0, "signals_pruned": 0, "carry_forward": True,
               "source_verified": False}
    ups.write_output(out, counts, [], l3_meta, l2_meta, dry_run=False)
    data = yaml.safe_load(out.read_text())
    assert "l3_meta" in data
    assert data["l3_meta"]["source_verified"] is False


def test_output_schema_valid_for_compute_balance_consumer(tmp_path):
    out = tmp_path / "signals.yaml"
    counts = {"claude": {"harness": 2, "engineering": 1, "data": 0, "other": 0},
              "codex": {"harness": 0, "engineering": 3, "data": 0, "other": 0},
              "gemini": {"harness": 0, "engineering": 0, "data": 0, "other": 0}}
    l2_meta = {"files_scanned": 3, "files_with_orchestrator": 3,
               "files_skipped_no_orchestrator": 0, "files_skipped_malformed": 0}
    ups.write_output(out, counts, [], {}, l2_meta, dry_run=False)
    data = yaml.safe_load(out.read_text())
    # Keys expected by compute-balance.py consumer
    assert "provider_activity" in data
    assert "capability_signals" in data
    assert "claude" in data["provider_activity"]
    assert "harness" in data["provider_activity"]["claude"]


# ── AC-5: nightly integration ─────────────────────────────────────────────────

def test_integrated_in_nightly_with_best_effort_call():
    nightly = REPO_ROOT / "scripts" / "cron" / "comprehensive-learning-nightly.sh"
    assert nightly.exists()
    text = nightly.read_text()
    assert "update-portfolio-signals.sh" in text
    assert "|| " in text  # best-effort pattern


def test_nightly_step_labels_are_monotonic():
    nightly = REPO_ROOT / "scripts" / "cron" / "comprehensive-learning-nightly.sh"
    text = nightly.read_text()
    import re
    labels = re.findall(r"# Step (\w+):", text)
    step_labels = [l for l in labels if l[0].isdigit()]
    # Find 3a, 3b, 3c in order
    idx_3a = next((i for i, l in enumerate(step_labels) if l == "3a"), -1)
    idx_3b = next((i for i, l in enumerate(step_labels) if l == "3b"), -1)
    idx_3c = next((i for i, l in enumerate(step_labels) if l == "3c"), -1)
    assert idx_3a != -1, "Step 3a missing"
    assert idx_3b != -1, "Step 3b missing"
    assert idx_3c != -1, "Step 3c missing"
    assert idx_3a < idx_3b < idx_3c, f"Steps not monotonic: {step_labels}"


# ── AC-6: shared state tracking policy ───────────────────────────────────────

def test_portfolio_signals_is_shared_repo_state_not_gitignored():
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", ".claude/state/portfolio-signals.yaml"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert tracked.returncode == 0, "portfolio-signals.yaml should be tracked shared state"

    ignored = subprocess.run(
        ["git", "check-ignore", ".claude/state/portfolio-signals.yaml"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert ignored.returncode != 0, "portfolio-signals.yaml should not be gitignored"
