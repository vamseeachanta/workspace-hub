"""Opt-in registry discovery using the existing freshness report pipeline.

Boundary basis: scripts/docs/staleness-scanner.py declares
FRESH_THRESHOLD_DAYS = 30 and MODERATE_THRESHOLD_DAYS = 90.
data/document-index/freshness-cadences.yaml, status_vocabulary and
source_of_truth_precedence, defines the shared status names and distinguishes
measured scanner age from expected per-asset cadence. These fixtures retain
scanner thresholds; they do not apply or change registry cadence policy.

Git timestamp lookups are mocked throughout this module. External-root cases
cover routing and dashboard isolation using ordinary temporary directories;
separate-repository Git integration remains untested.
"""
from __future__ import annotations

import importlib.util
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
# Reuse the fixed UTC observation date in test_staleness_scanner.py. All ages
# below are independent calendar-day subtractions from this observation date.
NOW = datetime.fromisoformat("2026-04-02T00:00:00+00:00")


@pytest.fixture
def scanner(monkeypatch, tmp_path):
    """Load the scanner with a fixed clock and mocked Git timestamp lookups."""
    spec = importlib.util.spec_from_file_location(
        "staleness_yaml_discovery", REPO_ROOT / "scripts/docs/staleness-scanner.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class FixedClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW if tz is None else NOW.astimezone(tz)

    monkeypatch.setattr(module, "datetime", FixedClock)
    monkeypatch.setattr(module, "REPO_ROOT", tmp_path / "repository")
    docs = module.REPO_ROOT / "docs"
    docs.mkdir(parents=True)
    monkeypatch.setattr(module, "DOCS_DIR", docs)
    monkeypatch.setattr(module, "DASHBOARD_PATH", docs / "dashboards/default.md")
    # The fixture never invokes Git. Calendar subtraction: April 2 minus
    # January 2 is 90 days, the scanner's STALE boundary cited above.
    monkeypatch.setattr(
        module, "get_git_last_modified",
        Mock(return_value="2026-01-02T00:00:00+00:00"),
    )
    return module


def test_yaml_registry_opt_in_reaches_dashboard(scanner):
    root = scanner.DOCS_DIR
    registry = root / "registry.yaml"
    registry.write_text("assets: []\n")
    (root / "index.md").write_text("# Index\n")
    (root / "nested").mkdir()
    short_registry = root / "nested/registry.yml"
    short_registry.write_text("assets: []\n")
    (root / "ignored.json").write_text("{}\n")

    # Reproduce the original omission before opting in.
    assert str(registry) not in scanner.scan_directory(str(root))
    discovered = scanner.scan_directory(str(root), include_yaml=True)
    assert discovered == sorted(
        str(path) for path in (registry, short_registry, root / "index.md")
    )
    entries = [scanner.classify_file(path, now=NOW) for path in discovered]
    report = scanner.build_yaml_report(entries, now=NOW)
    dashboard = scanner.generate_markdown_dashboard(report)
    for path in (registry, short_registry):
        relative = path.relative_to(scanner.REPO_ROOT)
        assert f"| `{relative}` | 90 | 2026-01-02 | git |" in dashboard
    assert [entry["file"] for entry in report["files"]] == [
        str(Path(path).relative_to(scanner.REPO_ROOT)) for path in discovered
    ]


def test_default_discovery_remains_markdown_only(scanner, capsys):
    markdown = scanner.DOCS_DIR / "index.md"
    markdown.write_text("# Index\n")
    for suffix in ("yaml", "yml"):
        (scanner.DOCS_DIR / f"registry.{suffix}").write_text("assets: []\n")

    assert scanner.scan_directory(str(scanner.DOCS_DIR)) == [str(markdown)]
    assert scanner.main([]) == 0
    dashboard = scanner.DASHBOARD_PATH.read_text()
    assert "`docs/index.md`" in dashboard
    assert "registry.yaml" not in dashboard
    assert "registry.yml" not in dashboard
    assert "Found 1 markdown files." in capsys.readouterr().out


# Independent calendar differences from April 2: March 4 = 29 days,
# March 3 = 30, January 3 = 89, January 2 = 90, January 1 = 91.
# Expected buckets follow the threshold declarations and vocabulary cited above.
@pytest.mark.parametrize(
    "stamp, age, status",
    [
        ("2026-03-04", 29, "FRESH"),
        ("2026-03-03", 30, "MODERATE"),
        ("2026-01-03", 89, "MODERATE"),
        ("2026-01-02", 90, "STALE"),
        ("2026-01-01", 91, "STALE"),
    ],
)
def test_yaml_age_threshold_boundaries(scanner, stamp, age, status):
    registry = scanner.DOCS_DIR / "registry.yaml"
    registry.write_text("assets: []\n")
    scanner.get_git_last_modified.return_value = f"{stamp}T00:00:00+00:00"
    entries = [
        scanner.classify_file(path, now=NOW)
        for path in scanner.scan_directory(str(scanner.DOCS_DIR), include_yaml=True)
    ]
    report = scanner.build_yaml_report(entries, now=NOW)
    # A single discovered fixture contributes one entry to its expected bucket.
    assert report["summary"][status] == len(entries) == 1
    assert entries[0]["age_days"] == age
    assert entries[0]["status"] == status
    dashboard = scanner.generate_markdown_dashboard(report)
    assert f"| `docs/registry.yaml` | {age} | {stamp} | git |" in dashboard


@pytest.mark.parametrize("external", [False, True])
def test_yaml_cli_writes_only_requested_dashboard(scanner, tmp_path, capsys, external):
    """Check mocked root routing and writes without creating a Git repository."""
    root = (tmp_path if external else scanner.REPO_ROOT) / "registries"
    root.mkdir()
    registry = root / "registry.yml"
    registry.write_text("assets: []\n")
    scanner.DASHBOARD_PATH.parent.mkdir(parents=True)
    scanner.DASHBOARD_PATH.write_text("preserve default dashboard\n")
    destination = tmp_path / "output/registry-dashboard.md"
    before = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}

    assert scanner.main([
        "--root", str(root), "--include-yaml", "--dashboard", str(destination),
    ]) == 0

    reported_path = str(registry) if external else "registries/registry.yml"
    assert f"| `{reported_path}` | 90 | 2026-01-02 | git |" in destination.read_text()
    after = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    assert after == {**before, destination: destination.read_bytes()}
    scanner.get_git_last_modified.assert_called_once_with(str(registry), repo_root=str(root))
    stdout = capsys.readouterr().out
    report_text = stdout.split("--- YAML Report ---", 1)[1].split("Dashboard written to:")[0]
    report = yaml.safe_load(report_text)
    assert report["files"][0]["file"] == reported_path
    assert report["files"][0]["status"] == "STALE"


@pytest.mark.parametrize("include_yaml", [False, True])
def test_custom_root_requires_dashboard_before_scanning(scanner, tmp_path, include_yaml):
    root = tmp_path / "registries"
    root.mkdir()
    (root / "registry.yaml").write_text("assets: []\n")
    args = ["--root", str(root)]
    if include_yaml:
        args.append("--include-yaml")
    with pytest.raises(SystemExit) as exc:
        scanner.main(args)
    # argparse documents status 2 for invalid arguments.
    assert exc.value.code == 2
    scanner.get_git_last_modified.assert_not_called()
    assert not scanner.DASHBOARD_PATH.exists()


@pytest.mark.parametrize("suffix", ["yaml", "yml"])
@pytest.mark.parametrize(
    "git_stamp, content, source, age, stamp",
    [
        ("2026-01-02T00:00:00+00:00", "Updated: 2026-03-03\n", "git", 90, "2026-01-02"),
        (None, "Updated: 2026-03-03\n", "content", 30, "2026-03-03"),
        ("invalid", "Updated: 2026-03-03\n", "content", 30, "2026-03-03"),
        (None, "assets: []\n", "filesystem", 29, "2026-03-04"),
        (None, "Updated: 2026-99-99\n", "filesystem", 29, "2026-03-04"),
    ],
)
def test_yaml_timestamp_precedence(scanner, suffix, git_stamp, content, source, age, stamp):
    # Calendar differences and thresholds have the same cited basis as the
    # boundary fixtures above. The newest mtime must not override Git/content.
    registry = scanner.DOCS_DIR / f"registry.{suffix}"
    registry.write_text(content)
    mtime = datetime.fromisoformat("2026-03-04T00:00:00+00:00").timestamp()
    os.utime(registry, (mtime, mtime))
    scanner.get_git_last_modified.return_value = git_stamp
    entry = scanner.classify_file(str(registry), now=NOW)
    assert entry["date_source"] == source
    assert entry["age_days"] == age
    report = scanner.build_yaml_report([entry], now=NOW)
    assert f"| `docs/registry.{suffix}` | {age} | {stamp} | {source} |" in scanner.generate_markdown_dashboard(report)


def test_yaml_discovery_handles_missing_root(scanner, tmp_path):
    assert scanner.scan_directory(str(tmp_path / "missing"), include_yaml=True) == []
