"""Tests for check_complexity_ratchet.py (WRK-1095).

TDD tests written before implementation:
  1. test_load_baseline — load and validate baseline YAML
  2. test_ratchet_pass — no count increase → PASS
  3. test_ratchet_fail_high_cc — D+ count increased → FAIL
  4. test_ratchet_fail_very_high_cc — E+ count increased → FAIL
  5. test_auto_update_baseline — improved repo auto-updates baseline
  6. test_bypass_reason_logged — SKIP_COMPLEXITY_REASON bypass is surfaced in output
"""

import sys
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

TESTS_DIR = Path(__file__).parent
SCRIPTS_QUALITY = TESTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_QUALITY))

import check_complexity_ratchet as rcr  # noqa: E402


def _make_baseline(tmp_path: Path, repos: dict) -> Path:
    """Write a minimal complexity-baseline.yaml and return its path."""
    data = {
        "schema_version": "1",
        "updated_at": "2026-03-10",
        "repos": repos,
    }
    p = tmp_path / "complexity-baseline.yaml"
    p.write_text(yaml.dump(data, default_flow_style=False))
    return p


# ---------------------------------------------------------------------------
# 1. Load baseline
# ---------------------------------------------------------------------------


def test_load_baseline(tmp_path):
    """Baseline YAML loads and validates without error."""
    baseline = _make_baseline(
        tmp_path,
        {
            "assethold": {
                "avg_cc": 3.07,
                "high_cc_count": 1,
                "very_high_cc_count": 1,
                "updated_at": "2026-03-10",
            }
        },
    )
    data = yaml.safe_load(baseline.read_text())
    assert data["schema_version"] == "1"
    assert "assethold" in data["repos"]
    err = rcr._validate_baseline(data)
    assert err is None, f"Unexpected validation error: {err}"


# ---------------------------------------------------------------------------
# 2. Ratchet pass — counts equal or decreased
# ---------------------------------------------------------------------------


def test_ratchet_pass():
    """PASS when actual counts are at or below baseline."""
    result = rcr.check_repo(
        repo="assethold",
        baseline={"high_cc_count": 1, "very_high_cc_count": 1},
        actual={"high_cc_count": 1, "very_high_cc_count": 0},
    )
    assert result["status"] == "pass"
    assert result["improved"] is True


# ---------------------------------------------------------------------------
# 3. Ratchet fail — D+ count increased
# ---------------------------------------------------------------------------


def test_ratchet_fail_high_cc():
    """FAIL when high_cc_count (D+) exceeds baseline."""
    result = rcr.check_repo(
        repo="worldenergydata",
        baseline={"high_cc_count": 39, "very_high_cc_count": 3},
        actual={"high_cc_count": 41, "very_high_cc_count": 3},
    )
    assert result["status"] == "fail"
    assert "high_cc_count" in result["message"].lower()


# ---------------------------------------------------------------------------
# 4. Ratchet fail — E+ count increased
# ---------------------------------------------------------------------------


def test_ratchet_fail_very_high_cc():
    """FAIL when very_high_cc_count (E+, CC>20) exceeds baseline."""
    result = rcr.check_repo(
        repo="digitalmodel",
        baseline={"high_cc_count": 72, "very_high_cc_count": 15},
        actual={"high_cc_count": 72, "very_high_cc_count": 16},
    )
    assert result["status"] == "fail"
    assert "very_high_cc_count" in result["message"].lower()


# ---------------------------------------------------------------------------
# 5. Auto-update baseline when complexity improves
# ---------------------------------------------------------------------------


def test_auto_update_baseline(tmp_path):
    """Baseline file is updated when actual counts are lower than baseline."""
    baseline_path = _make_baseline(
        tmp_path,
        {
            "assethold": {
                "avg_cc": 3.07,
                "high_cc_count": 5,
                "very_high_cc_count": 2,
                "updated_at": "2026-03-01",
            }
        },
    )
    improved = {"assethold": {"high_cc_count": 3, "very_high_cc_count": 1}}
    existing = yaml.safe_load(baseline_path.read_text())
    rcr._write_baseline(baseline_path, improved, existing)

    updated = yaml.safe_load(baseline_path.read_text())
    assert updated["repos"]["assethold"]["high_cc_count"] == 3
    assert updated["repos"]["assethold"]["very_high_cc_count"] == 1


# ---------------------------------------------------------------------------
# 6. Bypass — SKIP_COMPLEXITY_REASON is surfaced in output (not silently swallowed)
# ---------------------------------------------------------------------------


def test_bypass_reason_logged(capsys):
    """SKIP_COMPLEXITY_REASON env var bypass surfaces the reason in stdout."""
    bypass = "CI environment — radon not installed"
    report = rcr._format_report(
        passes=[],
        failures=[],
        bypass_reason=bypass,
        timestamp="2026-03-10T09:00:00Z",
    )
    assert "BYPASSED" in report
    assert bypass in report
