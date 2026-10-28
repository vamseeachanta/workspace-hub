"""Tests for module_status_matrix.py — TDD: written before implementation.

Tests cover:
  - Package scanning (discovers top-level packages under src/digitalmodel/)
  - Maturity classification (PRODUCTION, DEVELOPMENT, SKELETON, GAP)
  - Markdown output format (table, summary, gap highlights)
  - JSON output format (structured data)
  - Docstring percentage calculation
  - Top-5 gap highlighting logic

Related: GitHub issue #1570
"""

import json
import sys
import textwrap
from pathlib import Path

import pytest

# Add scripts/analysis to path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "analysis"))


@pytest.fixture
def sample_dm_repo(tmp_path):
    """Create a minimal digitalmodel-like repo structure for testing."""
    dm = tmp_path / "src" / "digitalmodel"
    dm.mkdir(parents=True)
    (dm / "__init__.py").write_text('"""digitalmodel root."""\n')

    # PRODUCTION: >5 test files, >3 source files, >50% docstrings
    prod = dm / "production_pkg"
    prod.mkdir()
    (prod / "__init__.py").write_text('"""Production package."""\n__all__ = ["Engine"]\n')
    for i in range(5):
        (prod / f"module_{i}.py").write_text(textwrap.dedent(f'''\
            """Module {i} docstring."""

            class Handler{i}:
                """Handler class."""
                def process(self):
                    pass

            def helper_{i}():
                """Helper function."""
                return {i}
        '''))
    tests_dir = tmp_path / "tests" / "production_pkg"
    tests_dir.mkdir(parents=True)
    for i in range(6):
        (tests_dir / f"test_module_{i}.py").write_text(f"def test_handler_{i}(): pass\n")

    # DEVELOPMENT: source files, 1-5 test files, files >20 lines
    dev = dm / "development_pkg"
    dev.mkdir()
    (dev / "__init__.py").write_text('"""Dev package."""\n')
    for i in range(4):
        filler = "\n".join(f"    attr_{j} = {j}" for j in range(20))
        (dev / f"core_{i}.py").write_text(textwrap.dedent(f'''\
            """Core {i} module with implementation."""

            class Core{i}:
                """Core handler {i}."""
            {filler}

                def process(self):
                    """Process data."""
                    return {i}

                def validate(self):
                    """Validate input."""
                    return True

            def setup_{i}():
                """Setup function."""
                return Core{i}()

            def teardown_{i}():
                """Teardown function."""
                pass
        '''))
    tests_dev = tmp_path / "tests" / "development_pkg"
    tests_dev.mkdir(parents=True)
    for i in range(3):
        (tests_dev / f"test_core_{i}.py").write_text(f"def test_core_{i}(): pass\n")

    # SKELETON: source files, 0 test files
    skel = dm / "skeleton_pkg"
    skel.mkdir()
    (skel / "__init__.py").write_text("")
    for i in range(3):
        (skel / f"stub_{i}.py").write_text(f"class Stub{i}:\n    pass\n\ndef do_thing_{i}():\n    pass\n")

    # GAP: only __init__.py
    gap = dm / "gap_pkg"
    gap.mkdir()
    (gap / "__init__.py").write_text("")

    # TINY: all files <20 lines with tests -> SKELETON
    tiny = dm / "tiny_pkg"
    tiny.mkdir()
    (tiny / "__init__.py").write_text("")
    (tiny / "small.py").write_text("x = 1\n")
    tests_tiny = tmp_path / "tests" / "tiny_pkg"
    tests_tiny.mkdir(parents=True)
    (tests_tiny / "test_small.py").write_text("def test_x(): pass\n")

    return tmp_path


@pytest.fixture
def promotion_repo(tmp_path):
    """Build independent target and control packages with hand-counted metrics."""
    # Policy: issues/1662; scripts/analysis/module_status_matrix.py:81-95.
    # Each package has four source files (including __init__.py), three with
    # module docstrings: 3 / 4 * 100 = 75%. The documented engine has one
    # docstring plus 20 assignment lines, so it exceeds the tiny-file cutoff.
    sources = {
        "__init__.py": '"""Synthetic package."""\n',
        "engine.py": '"""Synthetic engine."""\n' + "\n".join(
            f"VALUE_{index} = {index}" for index in range(20)
        ) + "\n",
        "api.py": '"""Synthetic interface."""\n',
        "settings.py": "ENABLED = True\n",
    }
    # Five literal test filenames keep the target and development control at
    # equality. Only the production control starts with the sixth test file.
    test_names = (
        "test_alpha.py", "test_beta.py", "test_gamma.py",
        "test_delta.py", "test_epsilon.py",
    )
    for name in ("target_pkg", "development_control", "production_control"):
        source_dir = tmp_path / "src" / "synthetic" / name
        source_dir.mkdir(parents=True)
        for filename, content in sources.items():
            (source_dir / filename).write_text(content)
        test_dir = tmp_path / "tests" / name
        test_dir.mkdir(parents=True)
        for filename in test_names:
            (test_dir / filename).write_text("def test_example(): pass\n")
    (tmp_path / "src" / "synthetic" / "__init__.py").write_text("")
    (tmp_path / "tests" / "production_control" / "test_zeta.py").write_text(
        "def test_example(): pass\n"
    )
    return tmp_path


# Strict production policy: issues/1662;
# scripts/analysis/module_status_matrix.py:81-95. Each row varies one metric
# immediately below, at, or above its threshold; the other metrics qualify.
@pytest.mark.parametrize(
    "file_count,test_count,docstring_pct,expected",
    [
        pytest.param(4, 4, 51, "DEVELOPMENT", id="tests-below"),
        pytest.param(4, 5, 51, "DEVELOPMENT", id="tests-equal"),
        pytest.param(4, 6, 51, "PRODUCTION", id="tests-above"),
        pytest.param(2, 6, 51, "DEVELOPMENT", id="sources-below"),
        pytest.param(3, 6, 51, "DEVELOPMENT", id="sources-equal"),
        pytest.param(4, 6, 51, "PRODUCTION", id="sources-above"),
        pytest.param(4, 6, 49, "DEVELOPMENT", id="docstrings-below"),
        pytest.param(4, 6, 50, "DEVELOPMENT", id="docstrings-equal"),
        pytest.param(4, 6, 51, "PRODUCTION", id="docstrings-above"),
    ],
)
def test_production_thresholds_are_strict(
    file_count, test_count, docstring_pct, expected,
):
    """Equality at any production threshold remains development."""
    from module_status_matrix import _classify_maturity

    assert _classify_maturity(
        file_count=file_count,
        test_count=test_count,
        docstring_pct=docstring_pct,
        all_files_tiny=False,
        only_init=False,
    ) == expected


def test_added_test_changes_only_target_maturity(promotion_repo):
    """Adding the sixth test promotes only the intended synthetic package."""
    from module_status_matrix import scan_packages

    before = {pkg["name"]: pkg for pkg in scan_packages(promotion_repo)}
    (promotion_repo / "tests" / "target_pkg" / "test_zeta.py").write_text(
        "def test_example(): pass\n"
    )
    after = {pkg["name"]: pkg for pkg in scan_packages(promotion_repo)}

    # Hand counts from promotion_repo, independent of the scanner: four source
    # files, three documented (75%), five tests before and six after addition.
    # Policy: issues/1662; scripts/analysis/module_status_matrix.py:81-95.
    def metrics(packages):
        return {
            name: (pkg["file_count"], pkg["test_count"],
                   pkg["docstring_pct"], pkg["status"])
            for name, pkg in packages.items()
        }

    assert metrics(before) == {
        "target_pkg": (4, 5, 75, "DEVELOPMENT"),
        "development_control": (4, 5, 75, "DEVELOPMENT"),
        "production_control": (4, 6, 75, "PRODUCTION"),
    }
    assert metrics(after) == {
        "target_pkg": (4, 6, 75, "PRODUCTION"),
        "development_control": (4, 5, 75, "DEVELOPMENT"),
        "production_control": (4, 6, 75, "PRODUCTION"),
    }
    for name in ("development_control", "production_control"):
        assert after[name] == before[name]


class TestPackageScanning:
    def test_discovers_all_packages(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        names = {p["name"] for p in packages}
        assert "production_pkg" in names
        assert "development_pkg" in names
        assert "skeleton_pkg" in names
        assert "gap_pkg" in names
        assert "tiny_pkg" in names

    def test_package_has_required_keys(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        required_keys = {"name", "status", "file_count", "test_count", "key_classes", "docstring_pct"}
        for pkg in packages:
            assert required_keys.issubset(pkg.keys())

    def test_file_count_accuracy(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        assert prod["file_count"] == 6  # 5 modules + __init__.py

    def test_test_count_accuracy(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        assert prod["test_count"] == 6


class TestMaturityClassification:
    def test_production_status(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        assert prod["status"] == "PRODUCTION"

    def test_development_status(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        dev = next(p for p in packages if p["name"] == "development_pkg")
        assert dev["status"] == "DEVELOPMENT"

    def test_skeleton_status(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        skel = next(p for p in packages if p["name"] == "skeleton_pkg")
        assert skel["status"] == "SKELETON"

    def test_gap_status(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        gap = next(p for p in packages if p["name"] == "gap_pkg")
        assert gap["status"] == "GAP"

    def test_tiny_files_classified_skeleton(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        tiny = next(p for p in packages if p["name"] == "tiny_pkg")
        assert tiny["status"] == "SKELETON"


class TestDocstringPercentage:
    def test_production_high_docstring_pct(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        assert prod["docstring_pct"] == 100

    def test_skeleton_zero_docstring_pct(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        skel = next(p for p in packages if p["name"] == "skeleton_pkg")
        assert skel["docstring_pct"] == 0


class TestKeyClasses:
    def test_key_classes_found(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        prod = next(p for p in packages if p["name"] == "production_pkg")
        assert len(prod["key_classes"]) >= 3

    def test_gap_has_no_classes(self, sample_dm_repo):
        from module_status_matrix import scan_packages
        packages = scan_packages(sample_dm_repo)
        gap = next(p for p in packages if p["name"] == "gap_pkg")
        assert len(gap["key_classes"]) == 0


class TestMarkdownOutput:
    def test_contains_table(self, sample_dm_repo):
        from module_status_matrix import generate_markdown
        packages = [
            {"name": "alpha", "status": "PRODUCTION", "file_count": 10,
             "test_count": 6, "key_classes": ["AlphaEngine"], "docstring_pct": 80},
        ]
        md = generate_markdown(packages)
        assert "| Package" in md
        assert "| alpha" in md
        assert "PRODUCTION" in md

    def test_contains_summary(self, sample_dm_repo):
        from module_status_matrix import generate_markdown
        packages = [
            {"name": "a", "status": "PRODUCTION", "file_count": 10,
             "test_count": 6, "key_classes": [], "docstring_pct": 80},
            {"name": "b", "status": "DEVELOPMENT", "file_count": 5,
             "test_count": 2, "key_classes": [], "docstring_pct": 40},
            {"name": "c", "status": "SKELETON", "file_count": 3,
             "test_count": 0, "key_classes": [], "docstring_pct": 0},
            {"name": "d", "status": "GAP", "file_count": 1,
             "test_count": 0, "key_classes": [], "docstring_pct": 0},
        ]
        md = generate_markdown(packages)
        assert "1 PRODUCTION" in md
        assert "1 DEVELOPMENT" in md
        assert "1 SKELETON" in md
        assert "1 GAP" in md

    def test_highlights_top_gaps(self, sample_dm_repo):
        from module_status_matrix import generate_markdown
        packages = [
            {"name": f"gap_{i}", "status": "SKELETON", "file_count": 20 - i,
             "test_count": 0, "key_classes": [], "docstring_pct": 0}
            for i in range(7)
        ]
        md = generate_markdown(packages)
        assert "gap_0" in md
        assert "Top" in md


class TestJSONOutput:
    def test_json_is_valid(self, sample_dm_repo):
        from module_status_matrix import generate_json_output
        packages = [
            {"name": "alpha", "status": "PRODUCTION", "file_count": 10,
             "test_count": 6, "key_classes": ["AlphaEngine"], "docstring_pct": 80},
        ]
        json_str = generate_json_output(packages)
        data = json.loads(json_str)
        assert "packages" in data
        assert "summary" in data
        assert len(data["packages"]) == 1

    def test_json_summary_counts(self, sample_dm_repo):
        from module_status_matrix import generate_json_output
        packages = [
            {"name": "a", "status": "PRODUCTION", "file_count": 10,
             "test_count": 6, "key_classes": [], "docstring_pct": 80},
            {"name": "b", "status": "GAP", "file_count": 1,
             "test_count": 0, "key_classes": [], "docstring_pct": 0},
        ]
        json_str = generate_json_output(packages)
        data = json.loads(json_str)
        assert data["summary"]["PRODUCTION"] == 1
        assert data["summary"]["GAP"] == 1


# Synthetic observation dates exercise UTC naming; no measured data is used.
FIRST_OBSERVATION = "2026-10-15T01:02:03.004005+00:00"
SECOND_OBSERVATION = "2026-10-15T01:02:04.004005+00:00"
FIRST_ARCHIVE = "module-status-matrix-20261015T010203.004005Z.json"
SECOND_ARCHIVE = "module-status-matrix-20261015T010204.004005Z.json"

# Independent hand calculation for the minimal CLI tree: one empty initializer,
# no tests, no docstrings and no nonblank lines => GAP, zero score and ratio.
GAP_SNAPSHOT = b'''{
  "packages": [
    {
      "name": "sample_pkg",
      "status": "GAP",
      "file_count": 1,
      "test_count": 0,
      "key_classes": [],
      "docstring_pct": 0,
      "loc": 0,
      "quality_score": 0.0,
      "test_source_ratio": 0.0
    }
  ],
  "summary": {
    "total": 1,
    "PRODUCTION": 0,
    "DEVELOPMENT": 0,
    "SKELETON": 0,
    "GAP": 1,
    "total_loc": 0,
    "avg_quality_score": 0.0
  }
}'''

# Adding one undocumented assignment gives two source files and one nonblank
# line, but still no tests => SKELETON, zero score and ratio.
SKELETON_SNAPSHOT = b'''{
  "packages": [
    {
      "name": "sample_pkg",
      "status": "SKELETON",
      "file_count": 2,
      "test_count": 0,
      "key_classes": [],
      "docstring_pct": 0,
      "loc": 1,
      "quality_score": 0.0,
      "test_source_ratio": 0.0
    }
  ],
  "summary": {
    "total": 1,
    "PRODUCTION": 0,
    "DEVELOPMENT": 0,
    "SKELETON": 1,
    "GAP": 0,
    "total_loc": 1,
    "avg_quality_score": 0.0
  }
}'''


@pytest.fixture
def archive_cli(tmp_path):
    """Run the real argument parser and entry point with a frozen UTC clock."""
    import subprocess

    repo = tmp_path / "repo"
    package = repo / "src" / "library" / "sample_pkg"
    package.mkdir(parents=True)
    (package.parent / "__init__.py").write_text("")
    (package / "__init__.py").write_text("")
    output = tmp_path / "output"
    history = tmp_path / "history"
    script = (
        Path(__file__).resolve().parents[2]
        / "scripts" / "analysis" / "module_status_matrix.py"
    )
    # runpy executes the shipped CLI as __main__; only clock and fault injection
    # are substituted. Scanning, serialization and filesystem writes stay real.
    driver = '''
import datetime
import os
import runpy
import sys
from unittest.mock import patch

script, observation, fail_archive = sys.argv[1:4]
instant = datetime.datetime.fromisoformat(observation)
class FrozenDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        assert tz is not None, "Observation clock must specify its timezone"
        return instant.astimezone(tz)
sys.argv = [script, *sys.argv[4:]]
with patch("datetime.datetime", FrozenDateTime):
    if fail_archive == "yes":
        with patch("os.link", side_effect=OSError("simulated archive-write failure")):
            runpy.run_path(script, run_name="__main__")
    else:
        runpy.run_path(script, run_name="__main__")
'''

    def run(*, archive=True, observation=FIRST_OBSERVATION, fail_archive=False):
        args = [str(repo), "--output-dir", str(output)]
        if archive:
            args.extend(["--history-dir", str(history)])
        return subprocess.run(
            [sys.executable, "-c", driver, str(script), observation,
             "yes" if fail_archive else "no", *args],
            cwd=tmp_path, capture_output=True, text=True, check=False,
        )

    return run, package, output, history


def test_archive_preserves_previous_observations(tmp_path):
    from datetime import datetime
    from module_status_matrix import archive_snapshot

    history = tmp_path / "nested" / "history"
    first = archive_snapshot(
        GAP_SNAPSHOT.decode("utf-8"), history,
        observed_at=datetime.fromisoformat(FIRST_OBSERVATION),
    )
    before = first.read_bytes()
    second = archive_snapshot(
        SKELETON_SNAPSHOT.decode("utf-8"), history,
        observed_at=datetime.fromisoformat(SECOND_OBSERVATION),
    )
    assert first.name == FIRST_ARCHIVE
    assert second.name == SECOND_ARCHIVE
    assert before == GAP_SNAPSHOT == first.read_bytes()
    assert second.read_bytes() == SKELETON_SNAPSHOT
    assert set(history.iterdir()) == {first, second}


def test_archive_identical_observation_is_noop(tmp_path):
    from datetime import datetime
    from module_status_matrix import archive_snapshot

    observation = datetime.fromisoformat(FIRST_OBSERVATION)
    first = archive_snapshot(GAP_SNAPSHOT.decode(), tmp_path, observed_at=observation)
    before = first.stat()
    repeated = archive_snapshot(GAP_SNAPSHOT.decode(), tmp_path, observed_at=observation)
    assert repeated == first
    assert first.read_bytes() == GAP_SNAPSHOT
    assert first.stat().st_mtime_ns == before.st_mtime_ns
    assert first.stat().st_ino == before.st_ino
    assert list(tmp_path.iterdir()) == [first]


def test_archive_name_collision_refuses(tmp_path):
    from datetime import datetime
    from module_status_matrix import archive_snapshot

    observation = datetime.fromisoformat(FIRST_OBSERVATION)
    first = archive_snapshot(GAP_SNAPSHOT.decode(), tmp_path, observed_at=observation)
    with pytest.raises(FileExistsError, match="different contents"):
        archive_snapshot(SKELETON_SNAPSHOT.decode(), tmp_path, observed_at=observation)
    assert first.read_bytes() == GAP_SNAPSHOT
    assert list(tmp_path.iterdir()) == [first]


def test_cli_history_directory_is_opt_in(archive_cli):
    run, _, output, history = archive_cli
    result = run(archive=False)
    assert result.returncode == 0, result.stderr
    assert not history.exists()
    assert {p.name for p in output.iterdir()} == {
        "module-status-matrix.json", "module-status-matrix.md",
    }
    assert (output / "module-status-matrix.json").read_bytes() == GAP_SNAPSHOT
    original_markdown = (output / "module-status-matrix.md").read_bytes()
    assert b"| sample_pkg" in original_markdown
    assert "| — |" in original_markdown.decode()
    result = run()
    assert result.returncode == 0, result.stderr
    assert (history / FIRST_ARCHIVE).read_bytes() == GAP_SNAPSHOT
    assert (output / "module-status-matrix.json").read_bytes() == GAP_SNAPSHOT
    assert "| → |" in (output / "module-status-matrix.md").read_text()


def test_cli_archives_generated_observations(archive_cli):
    run, package, output, history = archive_cli
    result = run()
    assert result.returncode == 0, result.stderr
    before = (history / FIRST_ARCHIVE).read_bytes()
    assert before == GAP_SNAPSHOT
    (package / "core.py").write_text("value = True\n")
    result = run(observation=SECOND_OBSERVATION)
    assert result.returncode == 0, result.stderr
    assert (history / FIRST_ARCHIVE).read_bytes() == before
    assert (history / SECOND_ARCHIVE).read_bytes() == SKELETON_SNAPSHOT
    assert (output / "module-status-matrix.json").read_bytes() == SKELETON_SNAPSHOT
    assert {p.name for p in history.iterdir()} == {FIRST_ARCHIVE, SECOND_ARCHIVE}


def test_archive_failure_preserves_active_snapshot(archive_cli):
    run, package, output, history = archive_cli
    result = run()
    assert result.returncode == 0, result.stderr
    previous_markdown = (output / "module-status-matrix.md").read_bytes()
    (package / "core.py").write_text("value = True\n")
    result = run(observation=SECOND_OBSERVATION, fail_archive=True)
    assert result.returncode != 0
    assert "simulated archive-write failure" in result.stderr
    assert (history / FIRST_ARCHIVE).read_bytes() == GAP_SNAPSHOT
    assert (output / "module-status-matrix.json").read_bytes() == GAP_SNAPSHOT
    assert (output / "module-status-matrix.md").read_bytes() == previous_markdown
    assert {p.name for p in history.iterdir()} == {FIRST_ARCHIVE}


def test_cli_collision_preserves_active_snapshot(archive_cli):
    run, package, output, history = archive_cli
    result = run()
    assert result.returncode == 0, result.stderr
    previous_markdown = (output / "module-status-matrix.md").read_bytes()
    (package / "core.py").write_text("value = True\n")
    result = run()
    assert result.returncode != 0
    assert "different contents" in result.stderr
    assert (history / FIRST_ARCHIVE).read_bytes() == GAP_SNAPSHOT
    assert (output / "module-status-matrix.json").read_bytes() == GAP_SNAPSHOT
    assert (output / "module-status-matrix.md").read_bytes() == previous_markdown
    assert {p.name for p in history.iterdir()} == {FIRST_ARCHIVE}


def test_cli_identical_observation_is_noop(archive_cli):
    run, _, output, history = archive_cli
    result = run()
    assert result.returncode == 0, result.stderr
    before = (history / FIRST_ARCHIVE).stat()
    result = run()
    assert result.returncode == 0, result.stderr
    assert (history / FIRST_ARCHIVE).stat().st_mtime_ns == before.st_mtime_ns
    assert (history / FIRST_ARCHIVE).read_bytes() == GAP_SNAPSHOT
    assert (output / "module-status-matrix.json").read_bytes() == GAP_SNAPSHOT
    assert {p.name for p in history.iterdir()} == {FIRST_ARCHIVE}


def test_archive_name_uses_utc_and_preserves_utf8(tmp_path):
    from datetime import datetime
    from module_status_matrix import archive_snapshot

    # Synthetic offset timestamp denotes the same instant as FIRST_OBSERVATION.
    observation = datetime.fromisoformat("2026-10-15T03:02:03.004005+02:00")
    snapshot = '{"trend": "↑"}\n'
    archive = archive_snapshot(snapshot, tmp_path, observed_at=observation)
    assert archive.name == FIRST_ARCHIVE
    assert archive.read_bytes() == snapshot.encode("utf-8")


@pytest.mark.parametrize(
    "existing", [GAP_SNAPSHOT, SKELETON_SNAPSHOT], ids=["identical", "conflicting"],
)
def test_archive_concurrent_name_reuse_never_overwrites(tmp_path, monkeypatch, existing):
    import os
    from datetime import datetime
    from module_status_matrix import archive_snapshot

    original_link = os.link

    def concurrent_link(source, destination):
        Path(destination).write_bytes(existing)
        original_link(source, destination)

    monkeypatch.setattr(os, "link", concurrent_link)
    observation = datetime.fromisoformat(FIRST_OBSERVATION)
    if existing == GAP_SNAPSHOT:
        archive_snapshot(GAP_SNAPSHOT.decode(), tmp_path, observed_at=observation)
    else:
        with pytest.raises(FileExistsError, match="different contents"):
            archive_snapshot(GAP_SNAPSHOT.decode(), tmp_path, observed_at=observation)
    assert (tmp_path / FIRST_ARCHIVE).read_bytes() == existing
    assert {p.name for p in tmp_path.iterdir()} == {FIRST_ARCHIVE}


def test_archive_partial_write_does_not_publish(tmp_path, monkeypatch):
    import tempfile
    from contextlib import contextmanager
    from datetime import datetime
    from module_status_matrix import archive_snapshot

    original_temporary_file = tempfile.NamedTemporaryFile

    @contextmanager
    def failing_temporary_file(*args, **kwargs):
        with original_temporary_file(*args, **kwargs) as stream:
            class PartialWrite:
                name = stream.name

                def write(self, data):
                    # One byte models a write that fails after making progress.
                    stream.write(data[:1])
                    raise OSError("simulated partial write")

            yield PartialWrite()

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", failing_temporary_file)
    with pytest.raises(OSError, match="simulated partial write"):
        archive_snapshot(
            GAP_SNAPSHOT.decode(), tmp_path,
            observed_at=datetime.fromisoformat(FIRST_OBSERVATION),
        )
    assert list(tmp_path.iterdir()) == []
