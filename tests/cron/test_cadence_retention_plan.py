"""Read-only retention contracts, Refs issues/2336.

Policy: keep 12 weekly, 12 monthly and 4 quarterly reports (issues/2336).
Period spelling follows scripts/cron/lib/cadence-common.sh:cadence_period().
The deliberately unordered examples below are independent hand calculations:
each tuple ends with its sole oldest period, after exactly the keep count of
newer periods. No expected candidate is calculated by the planner.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


PLANNER = Path(__file__).resolve().parents[2] / "scripts/cron/cadence_retention.py"
EXAMPLES = [
    (
        "weekly", 12,
        ("2026-W07", "2026-W01", "2026-W12", "2026-W03", "2026-W11",
         "2026-W02", "2026-W09", "2026-W05", "2026-W10", "2026-W04",
         "2026-W08", "2026-W06", "2025-W52"),
        "2025-W52",
    ),
    (
        "monthly", 12,
        ("2025-10", "2026-02", "2025-03", "2025-09", "2025-04", "2025-12",
         "2025-06", "2026-01", "2025-08", "2025-11", "2025-05", "2025-07",
         "2025-02"),
        "2025-02",
    ),
    (
        "quarterly", 4,
        ("2025-Q4", "2025-Q2", "2026-Q1", "2025-Q3", "2025-Q1"),
        "2025-Q1",
    ),
]


def config_for(cadence, keep, pattern="health-{period}.md"):
    return {"reports": [{"pattern": pattern, "cadence": cadence, "keep": keep}]}


def invoke(tmp_path, config, root=None, extra=()):
    root = root if root is not None else tmp_path / "reports"
    root.mkdir(exist_ok=True)
    config_path = tmp_path / "retention.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(PLANNER), "--report-root", str(root),
         "--config", str(config_path), *extra],
        text=True, capture_output=True, check=False,
    )


def make_reports(root, periods, prefix="health-"):
    root.mkdir(parents=True, exist_ok=True)
    for period in periods:
        (root / f"{prefix}{period}.md").write_text(period, encoding="utf-8")


def records(result):
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    return json.loads(result.stdout)


@pytest.mark.parametrize("cadence,keep,periods,oldest", EXAMPLES)
@pytest.mark.parametrize("boundary", ["below", "exact", "over"])
def test_retention_boundary_counts(tmp_path, cadence, keep, periods, oldest, boundary):
    # Hand calculation: keep-1, keep and keep+1 give zero, zero and one candidate.
    chosen = {"below": periods[:keep - 1], "exact": periods[:keep], "over": periods}
    make_reports(tmp_path / "reports", chosen[boundary])
    expected = [] if boundary != "over" else [{
        "source": f"health-{oldest}.md",
        "destination": f"archive/2025/health-{oldest}.md",
    }]
    assert records(invoke(tmp_path, config_for(cadence, keep))) == expected


@pytest.mark.parametrize("cadence,keep,periods,oldest", EXAMPLES)
def test_retention_ignores_mtime_and_input_order(tmp_path, cadence, keep, periods, oldest):
    first = tmp_path / "first"
    second = tmp_path / "second"
    make_reports(first, periods)
    make_reports(second, reversed(periods))
    # Synthetic epoch seconds: the oldest filename gets the newest mtime.
    for root in (first, second):
        for path in root.iterdir():
            timestamp = 200 if oldest in path.name else 100
            os.utime(path, (timestamp, timestamp))
    left = invoke(tmp_path, config_for(cadence, keep), first)
    right = invoke(tmp_path, config_for(cadence, keep), second)
    assert records(left) == [{
        "source": f"health-{oldest}.md",
        "destination": f"archive/2025/health-{oldest}.md",
    }]
    assert left.stdout == right.stdout


def test_retention_registry_order_is_irrelevant(tmp_path):
    # Hand calculation with keep=0: every registered report is a candidate.
    root = tmp_path / "reports"
    make_reports(root, ["2026-02"], "z-")
    make_reports(root, ["2025-Q4"], "a-")
    monthly = config_for("monthly", 0, "z-{period}.md")["reports"][0]
    quarterly = config_for("quarterly", 0, "a-{period}.md")["reports"][0]
    left = invoke(tmp_path, {"reports": [monthly, quarterly]})
    right = invoke(tmp_path, {"reports": [quarterly, monthly]})
    assert records(left) == [
        {"source": "a-2025-Q4.md", "destination": "archive/2025/a-2025-Q4.md"},
        {"source": "z-2026-02.md", "destination": "archive/2026/z-2026-02.md"},
    ]
    assert left.stdout == right.stdout


@pytest.mark.parametrize("period", [
    "2026-W00", "2026-W54", "2026-W1", "2026-00", "2026-13", "2026-1",
    "2026-Q0", "2026-Q5", "2026-Q01", "0000-Q1", "2026-Q1-extra",
    "２０２６-Q1", "2026-Q1\n", "latest",
])
def test_retention_rejects_malformed_periods(tmp_path, period):
    cadence = "weekly" if "W" in period else "monthly" if "Q" not in period else "quarterly"
    make_reports(tmp_path / "reports", [period])
    result = invoke(tmp_path, config_for(cadence, 12))
    assert result.returncode != 0
    assert result.stdout == ""
    assert "period" in result.stderr


@pytest.mark.parametrize("pattern", [
    "../health-{period}.md", "nested/../../health-{period}.md",
    "/health-{period}.md", "nested\\health-{period}.md",
    "*/health-{period}.md", "health-*.md", "health-{period}-{period}.md",
    "{period}/health.md", "./health-{period}.md", "archive/health-{period}.md",
    "nested//health-{period}.md", "health-{other}.md", "health-[{period}].md",
])
def test_retention_rejects_escaping_patterns(tmp_path, pattern):
    result = invoke(tmp_path, config_for("weekly", 12, pattern))
    assert result.returncode != 0
    assert result.stdout == ""
    assert "pattern" in result.stderr


@pytest.mark.parametrize("kind", [
    "file-link", "dangling-link", "directory-link", "root-link",
    "archive-link", "year-link", "non-file", "destination-exists",
])
def test_retention_rejects_unsafe_candidates(tmp_path, kind):
    root = tmp_path / "reports"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    name = "health-2025-Q1.md"
    pattern = "health-{period}.md"
    if kind in ("file-link", "dangling-link"):
        target = outside / name
        if kind == "file-link":
            target.write_text("unrelated", encoding="utf-8")
        (root / name).symlink_to(target)
    elif kind == "directory-link":
        make_reports(outside, ["2025-Q1"])
        (root / "nested").symlink_to(outside, target_is_directory=True)
        pattern = "nested/health-{period}.md"
    elif kind == "root-link":
        make_reports(outside, ["2025-Q1"])
        root = tmp_path / "linked-reports"
        root.symlink_to(outside, target_is_directory=True)
    elif kind in ("archive-link", "year-link", "destination-exists"):
        make_reports(root, ["2025-Q1"])
        if kind == "archive-link":
            (root / "archive").symlink_to(outside, target_is_directory=True)
        else:
            (root / "archive").mkdir()
            if kind == "year-link":
                (root / "archive/2025").symlink_to(outside, target_is_directory=True)
            else:
                make_reports(root / "archive/2025", ["2025-Q1"])
    else:
        (root / name).mkdir()
    # Zero keeps makes the single valid period old; symlinks always fail closed.
    result = invoke(tmp_path, config_for("quarterly", 0, pattern), root)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "retention:" in result.stderr


def test_retention_rejects_retained_symlink(tmp_path):
    root = tmp_path / "reports"
    root.mkdir()
    (root / "health-2026-Q1.md").symlink_to(tmp_path / "missing")
    result = invoke(tmp_path, config_for("quarterly", 4))
    assert result.returncode != 0
    assert result.stdout == ""
    assert "retention:" in result.stderr


def test_retention_rejects_duplicate_destinations(tmp_path):
    root = tmp_path / "reports"
    make_reports(root / "first", ["2025-Q1"])
    make_reports(root / "second", ["2025-Q1"])
    config = {"reports": [
        {"pattern": "first/health-{period}.md", "cadence": "quarterly", "keep": 0},
        {"pattern": "second/health-{period}.md", "cadence": "quarterly", "keep": 0},
    ]}
    result = invoke(tmp_path, config)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "duplicate" in result.stderr


def test_retention_rejects_overlapping_registrations(tmp_path):
    make_reports(tmp_path / "reports", ["2025-Q1"])
    entry = config_for("quarterly", 4)["reports"][0]
    result = invoke(tmp_path, {"reports": [entry, entry]})
    assert result.returncode != 0
    assert result.stdout == ""
    assert "duplicate" in result.stderr


def test_retention_multiple_older_periods_and_independent_counts(tmp_path):
    # issues/2336 keeps four quarterly periods for EACH registration.
    # Hand calculation: a has four newer periods plus these three old periods;
    # b has one period and stays below its own limit, irrespective of a's count.
    root = tmp_path / "reports"
    make_reports(root, ["2026-Q1", "2025-Q3", "2025-Q2", "2025-Q4",
                        "2024-Q4", "2025-Q1", "2024-Q3"], "a-")
    make_reports(root / "nested", ["2024-Q1"], "b-")
    config = {"reports": [
        {"pattern": "a-{period}.md", "cadence": "quarterly", "keep": 4},
        {"pattern": "nested/b-{period}.md", "cadence": "quarterly", "keep": 4},
    ]}
    assert records(invoke(tmp_path, config)) == [
        {"source": "a-2024-Q3.md", "destination": "archive/2024/a-2024-Q3.md"},
        {"source": "a-2024-Q4.md", "destination": "archive/2024/a-2024-Q4.md"},
        {"source": "a-2025-Q1.md", "destination": "archive/2025/a-2025-Q1.md"},
    ]


def test_retention_nested_source_with_empty_suffix(tmp_path):
    root = tmp_path / "reports"
    (root / "nested").mkdir(parents=True)
    (root / "nested/2025-Q1").write_text("report", encoding="utf-8")
    # Hand calculation with keep=0: the sole registered report is selected.
    assert records(invoke(tmp_path, config_for("quarterly", 0, "nested/{period}"))) == [
        {"source": "nested/2025-Q1", "destination": "archive/2025/2025-Q1"},
    ]


def test_retention_accepts_calendar_year_iso_week_spelling(tmp_path):
    # cadence_period(): %Y-W%V yields 2021-W53 on the first day of 2021,
    # although ISO week 53 belongs to the preceding ISO year.
    make_reports(tmp_path / "reports", ["2021-W53"])
    assert records(invoke(tmp_path, config_for("weekly", 0))) == [
        {"source": "health-2021-W53.md", "destination": "archive/2021/health-2021-W53.md"},
    ]


@pytest.mark.parametrize("config", [
    {"reports": []}, config_for("quarterly", 4, "missing/health-{period}.md"),
])
def test_retention_empty_registry_or_missing_subdirectory(tmp_path, config):
    assert records(invoke(tmp_path, config)) == []


def test_retention_rejects_missing_root_without_creating_it(tmp_path):
    config_path = tmp_path / "retention.json"
    config_path.write_text(json.dumps({"reports": []}), encoding="utf-8")
    root = tmp_path / "missing"
    result = subprocess.run(
        [sys.executable, str(PLANNER), "--report-root", str(root),
         "--config", str(config_path)], text=True, capture_output=True, check=False,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert "retention:" in result.stderr
    assert not root.exists()


@pytest.mark.parametrize("config", [
    [], {}, {"reports": "all"}, {"reports": [None]},
    config_for("daily", 12), config_for("weekly", -1), config_for("weekly", True),
    config_for("weekly", 1.5), config_for("weekly", "12"),
    {"reports": [{"pattern": "health-{period}.md", "cadence": "weekly"}]},
    {"reports": [{"pattern": "health-{period}.md", "cadence": "weekly", "keep": 12,
                  "apply": True}]},
    {"reports": [], "apply": True},
])
def test_retention_rejects_malformed_config(tmp_path, config):
    result = invoke(tmp_path, config)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "retention:" in result.stderr


@pytest.mark.parametrize("raw", [
    '{"reports": [], "reports": []}', '{"reports": [], "extra": NaN}', '{',
])
def test_retention_rejects_invalid_json(tmp_path, raw):
    config_path = tmp_path / "bad.json"
    config_path.write_text(raw, encoding="utf-8")
    root = tmp_path / "reports"
    root.mkdir()
    result = subprocess.run(
        [sys.executable, str(PLANNER), "--report-root", str(root),
         "--config", str(config_path)], text=True, capture_output=True, check=False,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert "retention:" in result.stderr


def snapshot(root):
    """Record content and write metadata; access times may change on reads."""
    return {
        path.relative_to(root).as_posix(): (
            path.lstat().st_mode, path.lstat().st_mtime_ns, path.lstat().st_ctime_ns,
            path.read_bytes() if path.is_file() else None,
        ) for path in (root, *root.rglob("*"))
    }


def test_retention_plan_changes_no_files(tmp_path):
    root = tmp_path / "reports"
    make_reports(root, ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1"])
    (root / "unregistered-2020-Q1.md").write_text("unrelated", encoding="utf-8")
    (root / "notes.txt").write_text("notes", encoding="utf-8")
    (root / "unregistered-link").symlink_to(tmp_path / "missing")
    make_reports(root / "archive/2024", ["2024-Q1"])
    config = config_for("quarterly", 4)
    (tmp_path / "retention.json").write_text(json.dumps(config), encoding="utf-8")
    before = snapshot(tmp_path)
    # Invoke without rewriting configuration to measure the entire fixture tree.
    command = [sys.executable, str(PLANNER), "--report-root", str(root),
               "--config", str(tmp_path / "retention.json")]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    assert records(result) == [{
        "source": "health-2025-Q1.md", "destination": "archive/2025/health-2025-Q1.md",
    }]
    assert snapshot(tmp_path) == before


def test_retention_requires_explicit_inputs_and_has_no_apply(tmp_path):
    result = subprocess.run(
        [sys.executable, str(PLANNER)], text=True, capture_output=True, check=False,
    )
    assert result.returncode != 0
    assert "--report-root" in result.stderr and "--config" in result.stderr
    result = invoke(tmp_path, {"reports": []}, extra=("--apply",))
    assert result.returncode != 0
    assert result.stdout == ""
    assert "unrecognized arguments" in result.stderr
