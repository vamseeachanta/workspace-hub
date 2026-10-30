"""Synthetic expectations are hand calculations, not results from the runner.

Timing fixtures sleep 0.12 s; the lower bound is 0.10 s to allow clock noise,
and the upper bound is 5 s to allow scheduling delays. These are test-only
engineering tolerances, not benchmark acceptance limits. Tiny budgets separate
PASS and SLOW without assuming that a workstation completes within one second.
"""

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[2] / "scripts/hygiene/reproduce_bench.py"
spec = importlib.util.spec_from_file_location("reproduce_bench", MODULE)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def git(repo, *args):
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    return subprocess.check_output(["git", "-C", str(repo), *args], env=env)


@pytest.fixture
def repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    return repo


def commit_fixture(repo, scripts, entries=None):
    """Fixture plumbing only: test repositories have no remotes or hooks."""
    for name, source in scripts.items():
        (repo / name).write_text(source, encoding="utf-8", newline="\n")
    if entries is None:
        entries = [entry(name) for name in scripts if name.endswith(".py")]
    (repo / "artifacts.registry.json").write_text(
        json.dumps(entries), encoding="utf-8", newline="\n"
    )
    for item in entries:
        (repo / item["path"]).parent.mkdir(parents=True, exist_ok=True)
        (repo / item["path"]).write_text("expected\n", encoding="utf-8", newline="\n")
    # Import synthetic fixture objects without configuring or overriding identity.
    stream = b"commit refs/heads/fixture\ncommitter Fixture <fixture> 0 +0000\ndata 7\nfixture\n"
    for file in sorted(repo.rglob("*")):
        if file.is_file() and ".git" not in file.relative_to(repo).parts:
            data = file.read_bytes()
            stream += (
                f"M 100644 inline {json.dumps(file.relative_to(repo).as_posix())}\ndata {len(data)}\n".encode()
                + data
                + b"\n"
            )
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    subprocess.run(
        ["git", "-C", str(repo), "fast-import", "--quiet"],
        input=stream + b"\ndone\n",
        check=True,
        env=env,
        capture_output=True,
    )
    git(repo, "symbolic-ref", "HEAD", "refs/heads/fixture")
    git(repo, "read-tree", "HEAD")
    return repo


def entry(script="build.py", **updates):
    return {
        "path": script.replace(".py", ".txt"),
        "kind": "text",
        "build": {"cwd": ".", "argv": [sys.executable, script]},
        "inputs": [script],
        **updates,
    }


def config(**updates):
    # Tests override repeats to keep subprocess fixtures short.
    return {"timeout_seconds": 5, "repeats": 1, "regression_ratio": 1.5, **updates}


def run(repo, tmp_path, **kwargs):
    return bench.benchmark(repo, config(**kwargs), temp_root=tmp_path / "builds")


@pytest.mark.parametrize(
    "source,settings,verdict",
    [
        (
            "from pathlib import Path; Path('build.txt').write_text('expected\\n', encoding=\"utf-8\", newline=\"\\n\")",
            {},
            "PASS",
        ),
        (
            "import time; time.sleep(.12); from pathlib import Path; Path('build.txt').write_text('expected\\n', encoding=\"utf-8\", newline=\"\\n\")",
            {"target_seconds": 0.001},
            "SLOW",
        ),
        (
            "from pathlib import Path; Path('build.txt').write_text('different', encoding=\"utf-8\", newline=\"\\n\")",
            {},
            "NOT_REPRODUCED",
        ),
        ("raise SystemExit(7)", {}, "FAILED"),
        ("import time; time.sleep(.12)", {"timeout_seconds": 0.01}, "TIMEOUT"),
        ("pass", {}, "NOT_REPRODUCED"),
    ],
)
def test_verdicts(repository, tmp_path, source, settings, verdict):
    commit_fixture(repository, {"build.py": source})
    before = git(repository, "status", "--porcelain")
    result = run(repository, tmp_path, **settings)
    item = result["artifacts"][0]
    assert item["verdict"] == verdict
    assert item["expected_sha256"] == hashlib.sha256(b"expected\n").hexdigest()
    assert git(repository, "status", "--porcelain") == before
    assert bench.exit_code(result) == (0 if verdict == "PASS" else 1)
    if verdict == "SLOW":
        assert 0.10 <= item["timing"]["median_seconds"] < 5
    if verdict == "FAILED":
        assert item["runs"][0]["exit_status"] == 7


def test_budget_overrides_target(repository, tmp_path):
    commit_fixture(
        repository,
        {
            "build.py": "from pathlib import Path; Path('build.txt').write_text('expected\\n', encoding=\"utf-8\", newline=\"\\n\")"
        },
        [entry(budget_seconds=5)],
    )
    item = run(repository, tmp_path, target_seconds=0.000001)["artifacts"][0]
    assert item["budget_seconds"] == 5
    assert item["verdict"] == "PASS"


def test_committed_snapshot_and_stale_cache(repository, tmp_path, monkeypatch):
    source = "from pathlib import Path; assert not Path('stale').exists(); Path('build.txt').write_text('expected\\n', encoding=\"utf-8\", newline=\"\\n\")"
    commit_fixture(repository, {"build.py": source})
    (repository / "stale").write_text(
        "ignored by tracked snapshot", encoding="utf-8", newline="\n"
    )
    (repository / "build.py").write_text(
        "raise SystemExit(8)", encoding="utf-8", newline="\n"
    )
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "unrelated"))
    assert run(repository, tmp_path)["artifacts"][0]["verdict"] == "PASS"
    assert (repository / "build.py").read_text(
        encoding="utf-8"
    ) == "raise SystemExit(8)"


@pytest.mark.parametrize("clean", [True, False])
def test_repeat_isolation_and_removed_output(repository, tmp_path, clean):
    source = "from pathlib import Path; p=Path('marker'); Path('build.txt').write_text('expected\\n', encoding=\"utf-8\", newline=\"\\n\") if not p.exists() else None; p.touch()"
    commit_fixture(repository, {"build.py": source})
    item = run(repository, tmp_path, repeats=2, clean_checkout=clean)["artifacts"][0]
    assert item["verdict"] == ("PASS" if clean else "NOT_REPRODUCED")
    assert [r["phase"] for r in item["runs"]] == ["cold", "warm"]


def fixed_runner(durations):
    """Clock pairs (0, d) give elapsed d by subtraction, independently of code."""
    ticks = iter(value for duration in durations for value in (0, duration))

    def runner(argv, *, cwd, **kwargs):
        Path(cwd, argv[-1].replace(".py", ".txt")).write_text(
            "expected\n", encoding="utf-8", newline="\n"
        )
        return subprocess.CompletedProcess(argv, 0)

    return runner, lambda: next(ticks)


def measured(repo, tmp_path, durations, **updates):
    runner, clock = fixed_runner(durations)
    return bench.benchmark(
        repo,
        config(repeats=3, **updates),
        temp_root=tmp_path / "builds",
        runner=runner,
        clock=clock,
    )


def test_statistics(repository, tmp_path):
    """[3,1,2] -> min 1, median 2, max 3; [8,4,6] -> 4,6,8.

    Total median = 2+6 = 8; longest single observation is second.txt at 8.
    Sorted [1,3,5,7] has even median (3+5)/2 = 4.
    """
    commit_fixture(repository, {"first.py": "pass", "second.py": "pass"})
    report = measured(repository, tmp_path, [3, 1, 2, 8, 4, 6])
    assert report["artifacts"][0]["timing"] == {
        "min_seconds": 1,
        "median_seconds": 2,
        "max_seconds": 3,
    }
    assert report["totals"] == {
        "sum_medians_seconds": 8,
        "longest_single_artifact": {"path": "second.txt", "seconds": 8},
    }
    assert bench.summarize([7, 1, 5, 3])["median_seconds"] == 4


def test_report_and_schema(repository, tmp_path):
    commit_fixture(repository, {"first.py": "pass", "second.py": "pass"})
    report = measured(repository, tmp_path, [3, 1, 2, 8, 4, 6], target_seconds=5)
    bench.validate_report(report)
    page = bench.render_html(report)
    for item in report["artifacts"]:
        assert item["path"] in page
        assert item["verdict"] in page
    assert "Method" in page and "Limits" in page
    assert "http://" not in page and "https://" not in page
    assert "hostname" not in json.dumps(report)
    for mutate in (
        lambda r: r.update(schema_version=999),
        lambda r: r["artifacts"][0]["timing"].update(median_seconds="wrong"),
        lambda r: r["artifacts"][0]["runs"][0].update(sha256="invalid"),
        lambda r: r.update(unknown=True),
    ):
        broken = json.loads(json.dumps(report))
        mutate(broken)
        with pytest.raises((ValueError, TypeError)):
            bench.validate_report(broken)


@pytest.fixture
def four_repeat_report(repository, tmp_path):
    """Issue #4223 synthetic case: two artifacts, four repeats = eight calls.

    Clock differences are [7,1,5,3] and [12,2,8,4] seconds; explicit budgets
    are 4 and 5 seconds. These are arithmetic inputs, not measured performance.
    """
    commit_fixture(
        repository,
        {"first.py": "pass", "second.py": "pass"},
        [entry("first.py", budget_seconds=4), entry("second.py", budget_seconds=5)],
    )
    runner, clock = fixed_runner([7, 1, 5, 3, 12, 2, 8, 4])
    calls = []

    def recording_runner(argv, **kwargs):
        calls.append(list(argv))
        return runner(argv, **kwargs)

    report = bench.benchmark(
        repository,
        config(repeats=4),
        temp_root=tmp_path / "builds",
        runner=recording_runner,
        clock=clock,
    )
    return report, calls


def test_four_repeat_report_uses_even_medians(four_repeat_report):
    """Hand calculation: [1,3,5,7] -> 1, (3+5)/2=4, 7;
    [2,4,8,12] -> 2, (4+8)/2=6, 12. Sum 4+6=10; longest is second at 12.
    """
    report, calls = four_repeat_report
    assert calls == [
        [sys.executable, "first.py"],
        [sys.executable, "first.py"],
        [sys.executable, "first.py"],
        [sys.executable, "first.py"],
        [sys.executable, "second.py"],
        [sys.executable, "second.py"],
        [sys.executable, "second.py"],
        [sys.executable, "second.py"],
    ]
    assert len(calls) == 8
    assert report["method"]["repeats"] == 4
    first, second = report["artifacts"]
    assert [first["path"], second["path"]] == ["first.txt", "second.txt"]
    assert [run["seconds"] for run in first["runs"]] == [7, 1, 5, 3]
    assert [run["seconds"] for run in second["runs"]] == [12, 2, 8, 4]
    for item in (first, second):
        assert len(item["runs"]) == 4
        assert [run["phase"] for run in item["runs"]] == [
            "cold", "warm", "warm", "warm"
        ]
        assert all(run["status"] == "PASS" for run in item["runs"])
    assert first["timing"] == {
        "min_seconds": 1,
        "median_seconds": 4,
        "max_seconds": 7,
    }
    assert second["timing"] == {
        "min_seconds": 2,
        "median_seconds": 6,
        "max_seconds": 12,
    }
    assert report["totals"] == {
        "sum_medians_seconds": 10,
        "longest_single_artifact": {"path": "second.txt", "seconds": 12},
    }
    bench.validate_report(json.loads(json.dumps(report)))


def test_four_repeat_verdicts_use_median_budget_boundary(four_repeat_report):
    """Hand calculation: median 4 equals budget 4 (PASS) despite max 7;
    median 6 exceeds budget 5 (SLOW), so the report exit is nonzero.
    """
    report, _ = four_repeat_report
    assert [
        (item["path"], item["budget_seconds"], item["verdict"])
        for item in report["artifacts"]
    ] == [("first.txt", 4, "PASS"), ("second.txt", 5, "SLOW")]
    assert bench.exit_code(report) != 0

    class Rows(HTMLParser):
        """Collect row text without depending on styling or nested markup."""

        def __init__(self):
            super().__init__()
            self.rows = []
            self.row = None

        def handle_starttag(self, tag, attrs):
            if tag == "tr":
                self.row = []

        def handle_data(self, data):
            if self.row is not None and data.strip():
                self.row.append(data.strip())

        def handle_endtag(self, tag):
            if tag == "tr" and self.row is not None:
                self.rows.append(self.row)
                self.row = None

    page = Rows()
    page.feed(bench.render_html(report))
    pairs = {
        (path, verdict)
        for row in page.rows
        for path in ("first.txt", "second.txt")
        for verdict in ("PASS", "SLOW")
        if path in row and verdict in row
    }
    assert pairs == {("first.txt", "PASS"), ("second.txt", "SLOW")}


@pytest.mark.parametrize(
    "previous,current,regression",
    [([2, 2, 2], [2, 2, 2], False), ([2, 2, 2], [4, 4, 4], True)],
)
def test_history(repository, tmp_path, previous, current, regression):
    """Prior median 2, threshold 2*1.5=3: current 2 is stable; 4 regresses."""
    commit_fixture(repository, {"build.py": "pass"})
    history = tmp_path / "history.jsonl"
    old = measured(repository, tmp_path, previous)
    bench.append_history(history, old)
    report = measured(repository, tmp_path, current)
    bench.compare_history(report, bench.read_history(history), window=3, ratio=1.5)
    item = report["artifacts"][0]
    assert item["regression"] is regression
    assert item["baseline_median_seconds"] == 2
    assert bench.exit_code(report) == int(regression)
    bench.append_history(history, report)
    assert len(bench.read_history(history)) == 2


def test_history_window_first_run_and_strict_threshold(repository, tmp_path):
    """Last two medians [2,4] -> (2+4)/2=3; 4.5 equals 3*1.5: no growth over limit."""
    commit_fixture(repository, {"build.py": "pass"})
    report = measured(repository, tmp_path, [4.5] * 3)
    bench.compare_history(report, [], window=2, ratio=1.5)
    assert report["artifacts"][0]["baseline_median_seconds"] is None
    prior = [measured(repository, tmp_path, [d] * 3) for d in (100, 2, 4)]
    bench.compare_history(report, prior, window=2, ratio=1.5)
    assert report["artifacts"][0]["baseline_median_seconds"] == 3
    assert not report["artifacts"][0]["regression"]


@pytest.mark.parametrize(
    "updates",
    [
        {"repeats": 0},
        {"repeats": True},
        {"target_seconds": -1},
        {"target_seconds": float("nan")},
        {"clean_checkout": "yes"},
        {"timeout_seconds": 0},
        {"unknown": 1},
    ],
)
def test_invalid_config(updates):
    with pytest.raises((ValueError, TypeError)):
        bench.parse_config(config(**updates))


@pytest.mark.parametrize(
    "path", ["../escape", "/absolute", "C:\\escape", ".git/config"]
)
def test_unsafe_registry_path(repository, tmp_path, path):
    commit_fixture(repository, {"build.py": "pass"})
    registry = [entry(path=path)]
    with pytest.raises((ValueError, TypeError)):
        bench.benchmark(
            repository, config(), registry=registry, temp_root=tmp_path / "builds"
        )


def test_html_escaping(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    report = measured(repository, tmp_path, [1] * 3)
    report["artifacts"][0]["path"] = '<img src=x onerror="bad">'
    assert "<img" not in bench.render_html(report)


def test_worked_example(tmp_path):
    """Guide example has 2 artifacts, 3 repeats each, so 6 successful builds."""
    guide = MODULE.with_name("REPRODUCE_BENCH.md").read_text(encoding="utf-8")
    source = guide.split("```python\n", 1)[1].split("\n```", 1)[0]
    env = dict(os.environ, TMPDIR=str(tmp_path), REPRODUCE_BENCH=str(MODULE))
    result = subprocess.run(
        [sys.executable, "-I", "-c", source],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert (
        result.stdout.strip() == "PASS: two artifacts; JSON, HTML and history written"
    )
    (root,) = tmp_path.glob("reproduce-example-*")
    report = json.loads((root / "output/report.json").read_text(encoding="utf-8"))
    bench.validate_report(report)
    assert len(report["artifacts"]) == 2
    assert sum(len(a["runs"]) for a in report["artifacts"]) == 6
    assert (root / "output/report.html").is_file()
    assert len(bench.read_history(root / "output/bench-history.jsonl")) == 1
    assert git(root / "repo", "status", "--porcelain") == b""


def cli(repo, tmp_path, settings, *args):
    config_path = tmp_path / "bench.json"
    config_path.write_text(
        json.dumps(config(**settings)), encoding="utf-8", newline="\n"
    )
    return subprocess.run(
        [
            sys.executable,
            "-I",
            str(MODULE),
            "--repo",
            str(repo),
            "--config",
            str(config_path),
            "--out",
            str(tmp_path / "report.json"),
            *args,
        ],
        check=False,
        env=dict(os.environ, TMPDIR=str(tmp_path)),
        capture_output=True,
        text=True,
    )


def test_cli_reports_history_and_regression(repository, tmp_path):
    """History median 0 has threshold 0*1.5=0; any positive subprocess time grows."""
    commit_fixture(
        repository,
        {
            "build.py": "from pathlib import Path; Path('build.txt').write_text('expected\\n', encoding=\"utf-8\", newline=\"\\n\")"
        },
    )
    settings = {"history": "history.jsonl", "history_window": 2}
    assert cli(repository, tmp_path, settings, "--compare", "history").returncode == 0
    history = bench.read_history(tmp_path / "history.jsonl")
    for item in history[0]["artifacts"]:
        for observation in item["runs"]:
            observation["seconds"] = 0
        item["timing"] = {"min_seconds": 0, "median_seconds": 0, "max_seconds": 0}
    history[0]["totals"] = {
        "sum_medians_seconds": 0,
        "longest_single_artifact": {"path": "build.txt", "seconds": 0},
    }
    (tmp_path / "history.jsonl").write_text(
        json.dumps(history[0]) + "\n", encoding="utf-8", newline="\n"
    )
    result = cli(repository, tmp_path, settings, "--compare", "history")
    assert result.returncode == 1
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["artifacts"][0]["regression"]
    assert len(bench.read_history(tmp_path / "history.jsonl")) == 2
    assert "REGRESSION" in (tmp_path / "report.html").read_text(encoding="utf-8")


def test_cli_rejects_in_repo_outputs(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    settings = tmp_path / "bench.json"
    settings.write_text(json.dumps(config()), encoding="utf-8", newline="\n")
    before = git(repository, "status", "--porcelain")
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(MODULE),
            "--repo",
            str(repository),
            "--config",
            str(settings),
            "--out",
            str(repository / "report.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert str(repository) not in result.stderr
    assert git(repository, "status", "--porcelain") == before


def test_history_skips_changed_basis(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    previous = measured(repository, tmp_path, [1] * 3)
    previous["artifacts"][0]["fingerprint"] = "0" * 64
    report = measured(repository, tmp_path, [5] * 3)
    bench.compare_history(report, [previous], window=2, ratio=1.5)
    assert report["artifacts"][0]["baseline_median_seconds"] is None
    assert not report["artifacts"][0]["regression"]


def test_subprocess_output_is_never_captured(repository, tmp_path):
    source = "print('synthetic-sensitive-output'); raise SystemExit(1)"
    commit_fixture(repository, {"build.py": source})
    result = cli(repository, tmp_path, {})
    assert result.returncode == 1
    assert not result.stdout and not result.stderr
    assert "synthetic-sensitive-output" not in (tmp_path / "report.json").read_text(
        encoding="utf-8"
    )


def test_schema_rejects_inconsistent_totals(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    report = measured(repository, tmp_path, [1, 2, 3])
    report["totals"]["sum_medians_seconds"] = 99
    with pytest.raises((ValueError, TypeError)):
        bench.validate_report(report)


def test_schema_rejects_false_pass(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    report = measured(repository, tmp_path, [1, 2, 3])
    report["artifacts"][0]["runs"][0]["sha256"] = "0" * 64
    with pytest.raises((ValueError, TypeError)):
        bench.validate_report(report)


def test_comparison_settings_recorded(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    report = measured(repository, tmp_path, [1] * 3)
    bench.compare_history(report, [], window=2, ratio=1.5)
    assert report["comparison"] == {
        "enabled": True,
        "history_window": 2,
        "regression_ratio": 1.5,
    }
    bench.validate_report(report)


def test_cli_does_not_overwrite_config(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    settings = tmp_path / "bench.json"
    settings.write_text(json.dumps(config()), encoding="utf-8", newline="\n")
    original = settings.read_bytes()
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            str(MODULE),
            "--repo",
            str(repository),
            "--config",
            str(settings),
            "--out",
            str(settings),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert settings.read_bytes() == original


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group timeout contract")
def test_timeout_kills_descendants(tmp_path):
    """A child writes after 0.3 s; timeout at 0.1 s must kill it first.

    After 0.5 s (>0.3 s) without the marker, no surviving child performed the write.
    These durations only order events and are not performance acceptance limits.
    """
    import time

    marker = tmp_path / "child-marker"
    child = f"import time; from pathlib import Path; time.sleep(.3); Path({str(marker)!r}).touch()"
    parent = f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child!r}]); time.sleep(2)"
    with pytest.raises(subprocess.TimeoutExpired):
        bench.run_process(
            [sys.executable, "-c", parent], cwd=tmp_path, timeout=0.1, env=os.environ
        )
    time.sleep(0.5)
    assert not marker.exists()


def test_registry_dot_prefixes(repository, tmp_path):
    commit_fixture(
        repository,
        {
            "build.py": "from pathlib import Path; Path('build.txt').write_text('expected\\n', encoding=\"utf-8\", newline=\"\\n\")"
        },
    )
    registry = [entry(path="./build.txt", inputs=["./build.py"])]
    report = bench.benchmark(
        repository, config(), registry=registry, temp_root=tmp_path / "builds"
    )
    assert report["artifacts"][0]["verdict"] == "PASS"
    assert report["artifacts"][0]["path"] == "build.txt"


def test_default_never_queries_hostname(repository, tmp_path, monkeypatch):
    def forbidden():
        raise AssertionError("hostname query must be opt-in")

    monkeypatch.setattr(bench.platform, "node", forbidden)
    commit_fixture(repository, {"build.py": "pass"})
    assert "hostname" not in measured(repository, tmp_path, [1] * 3)["machine"]


def test_schema_rejects_invalid_timestamp(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    report = measured(repository, tmp_path, [1] * 3)
    report["recorded_at"] = "invalid"
    with pytest.raises((ValueError, TypeError)):
        bench.validate_report(report)


@pytest.mark.parametrize("staged", ["deletion", "addition", "modification"])
def test_snapshot_membership_ignores_index(repository, tmp_path, staged):
    commit_fixture(
        repository,
        {
            "build.py": "from pathlib import Path; Path('build.txt').write_bytes(b'expected\\n')"
        },
    )
    revision = git(repository, "rev-parse", "HEAD").decode().strip()
    if staged == "deletion":
        git(
            repository,
            "rm",
            "--cached",
            "artifacts.registry.json",
            "build.py",
            "build.txt",
        )
    elif staged == "addition":
        (repository / "uncommitted.txt").write_text(
            "not committed", encoding="utf-8", newline="\n"
        )
        git(repository, "add", "uncommitted.txt")
    else:
        (repository / "artifacts.registry.json").write_text(
            "[]", encoding="utf-8", newline="\n"
        )
        git(repository, "add", "artifacts.registry.json")
    status_before = git(repository, "status", "--porcelain")
    index_before = (repository / ".git/index").read_bytes()
    report = run(repository, tmp_path)
    assert report["revision"] == revision
    assert report["artifacts"][0]["verdict"] == "PASS"
    assert set(bench.tracked_entries(repository)) == {
        "artifacts.registry.json",
        "build.py",
        "build.txt",
    }
    assert (repository / ".git/index").read_bytes() == index_before
    assert git(repository, "status", "--porcelain") == status_before


@pytest.mark.parametrize("linked", [False, True])
def test_output_reparse_directory(repository, tmp_path, monkeypatch, linked):
    """A rebuilt file beneath a reparse directory cannot establish reproduction."""
    from types import SimpleNamespace

    commit_fixture(repository, {"build.py": "pass"})
    original = Path.lstat
    rebuilt = False

    def lstat(path, *args, **kwargs):
        metadata = original(path, *args, **kwargs)
        if linked and rebuilt and path.name == "0":
            return SimpleNamespace(st_mode=metadata.st_mode, st_file_attributes=0x400)
        return metadata

    def runner(argv, *, cwd, timeout, env):
        nonlocal rebuilt
        Path(cwd, "build.txt").write_bytes(b"expected\n")
        rebuilt = True
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(Path, "lstat", lstat)
    result = bench.benchmark(
        repository, config(), temp_root=tmp_path / "builds", runner=runner
    )
    assert result["artifacts"][0]["verdict"] == ("NOT_REPRODUCED" if linked else "PASS")


@pytest.mark.parametrize("location", ["checkout", "parent"])
@pytest.mark.parametrize("directory_output", [False, True])
def test_repeat_cleanup_rejects_linked_ancestors(
    repository, tmp_path, monkeypatch, location, directory_output
):
    """Two repeats must preserve external bytes and directory contents."""
    artifact = "build.txt" if location == "checkout" else "nested/build.txt"
    commit_fixture(repository, {"build.py": "pass"}, [entry(path=artifact)])
    external = tmp_path / "external"
    external.mkdir()
    protected = external / "build.txt"
    if directory_output:
        protected.mkdir()
        protected = protected / "sentinel.txt"
    protected.write_bytes(b"retained")
    attempts = []
    calls = []
    original_unlink = Path.unlink
    original_rmtree = bench.shutil.rmtree

    def unlink(path, *args, **kwargs):
        if path.resolve().is_relative_to(external):
            attempts.append("unlink")
            raise OSError("external cleanup intercepted")
        return original_unlink(path, *args, **kwargs)

    def rmtree(path, *args, **kwargs):
        if Path(path).resolve().is_relative_to(external):
            attempts.append("rmtree")
            raise OSError("external cleanup intercepted")
        return original_rmtree(path, *args, **kwargs)

    def runner(argv, *, cwd, **kwargs):
        calls.append(True)
        parent = cwd if location == "checkout" else cwd / "nested"
        parent.rename(parent.with_name(parent.name + "-saved"))
        parent.symlink_to(external, target_is_directory=True)
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(Path, "unlink", unlink)
    monkeypatch.setattr(bench.shutil, "rmtree", rmtree)
    with pytest.raises(ValueError, match="linked snapshot path"):
        bench.benchmark(
            repository,
            config(repeats=2, clean_checkout=False),
            temp_root=tmp_path / "builds",
            runner=runner,
        )
    assert calls == [True]
    assert attempts == []
    assert protected.read_bytes() == b"retained"
    assert sorted(p.relative_to(external).as_posix() for p in external.rglob("*")) == (
        ["build.txt", "build.txt/sentinel.txt"] if directory_output else ["build.txt"]
    )


@pytest.mark.parametrize("missing", ["repeats", "regression_ratio"])
def test_explicit_performance_settings_required(missing):
    settings = {"timeout_seconds": 5, "repeats": 3, "regression_ratio": 1.5}
    del settings[missing]
    with pytest.raises(ValueError, match=missing):
        bench.parse_config(settings)


def test_explicit_performance_settings_preserved():
    settings = {"timeout_seconds": 5, "repeats": 4, "regression_ratio": 1.25}
    result = bench.parse_config(settings)
    assert result["repeats"] == 4
    assert result["regression_ratio"] == 1.25


@pytest.mark.parametrize("location", ["checkout", "parent"])
def test_repeat_cleanup_rejects_reparse_ancestors(
    repository, tmp_path, monkeypatch, location
):
    """Simulated junction metadata must stop reuse before any output deletion."""
    from types import SimpleNamespace

    artifact = "build.txt" if location == "checkout" else "nested/build.txt"
    commit_fixture(repository, {"build.py": "pass"}, [entry(path=artifact)])
    original = Path.lstat
    marked = []

    def lstat(path, *args, **kwargs):
        metadata = original(path, *args, **kwargs)
        if path in marked:
            return SimpleNamespace(st_mode=metadata.st_mode, st_file_attributes=0x400)
        return metadata

    def runner(argv, *, cwd, **kwargs):
        assert not marked, "linked checkout must not run again"
        output = cwd / artifact
        output.write_bytes(b"retained")
        marked.append(cwd if location == "checkout" else output.parent)
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(Path, "lstat", lstat)
    with pytest.raises(ValueError, match="linked snapshot path"):
        bench.benchmark(
            repository,
            config(repeats=2, clean_checkout=False),
            temp_root=tmp_path / "builds",
            runner=runner,
        )
