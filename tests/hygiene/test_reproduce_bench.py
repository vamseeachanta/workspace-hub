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
        (repo / name).write_text(source)
    if entries is None:
        entries = [entry(name) for name in scripts if name.endswith(".py")]
    (repo / "artifacts.registry.json").write_text(json.dumps(entries))
    for item in entries:
        (repo / item["path"]).write_text("expected\n")
    # Import synthetic fixture objects without configuring or overriding identity.
    stream = b"commit refs/heads/fixture\ncommitter Fixture <fixture> 0 +0000\ndata 7\nfixture\n"
    for file in sorted(repo.iterdir()):
        if file.is_file():
            data = file.read_bytes()
            stream += (
                f"M 100644 inline {json.dumps(file.name)}\ndata {len(data)}\n".encode()
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
    # Task specification, slices 1 and 4: 60 s, 3 repeats, ratio 1.5.
    return {"timeout_seconds": 5, "repeats": 1, **updates}


def run(repo, tmp_path, **kwargs):
    return bench.benchmark(repo, config(**kwargs), temp_root=tmp_path / "builds")


@pytest.mark.parametrize(
    "source,settings,verdict",
    [
        (
            "from pathlib import Path; Path('build.txt').write_text('expected\\n')",
            {},
            "PASS",
        ),
        (
            "import time; time.sleep(.12); from pathlib import Path; Path('build.txt').write_text('expected\\n')",
            {"target_seconds": 0.001},
            "SLOW",
        ),
        (
            "from pathlib import Path; Path('build.txt').write_text('different')",
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
            "build.py": "from pathlib import Path; Path('build.txt').write_text('expected\\n')"
        },
        [entry(budget_seconds=5)],
    )
    item = run(repository, tmp_path, target_seconds=0.000001)["artifacts"][0]
    assert item["budget_seconds"] == 5
    assert item["verdict"] == "PASS"


def test_committed_snapshot_and_stale_cache(repository, tmp_path, monkeypatch):
    source = "from pathlib import Path; assert not Path('stale').exists(); Path('build.txt').write_text('expected\\n')"
    commit_fixture(repository, {"build.py": source})
    (repository / "stale").write_text("ignored by tracked snapshot")
    (repository / "build.py").write_text("raise SystemExit(8)")
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "unrelated"))
    assert run(repository, tmp_path)["artifacts"][0]["verdict"] == "PASS"
    assert (repository / "build.py").read_text() == "raise SystemExit(8)"


@pytest.mark.parametrize("clean", [True, False])
def test_repeat_isolation_and_removed_output(repository, tmp_path, clean):
    source = (
        "from pathlib import Path; p=Path('marker'); "
        "Path('build.txt').write_text('expected\\n') if not p.exists() else None; "
        "p.touch()"
    )
    commit_fixture(repository, {"build.py": source})
    item = run(repository, tmp_path, repeats=2, clean_checkout=clean)["artifacts"][0]
    assert item["verdict"] == ("PASS" if clean else "NOT_REPRODUCED")
    assert [r["phase"] for r in item["runs"]] == ["cold", "warm"]


def fixed_runner(durations):
    """Clock pairs (0, d) give elapsed d by subtraction, independently of code."""
    ticks = iter(value for duration in durations for value in (0, duration))

    def runner(argv, *, cwd, **kwargs):
        Path(cwd, argv[-1].replace(".py", ".txt")).write_text("expected\n")
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
    guide = MODULE.with_name("REPRODUCE_BENCH.md").read_text()
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
    report = json.loads((root / "output/report.json").read_text())
    bench.validate_report(report)
    assert len(report["artifacts"]) == 2
    assert sum(len(a["runs"]) for a in report["artifacts"]) == 6
    assert (root / "output/report.html").is_file()
    assert len(bench.read_history(root / "output/bench-history.jsonl")) == 1
    assert git(root / "repo", "status", "--porcelain") == b""


def cli(repo, tmp_path, settings, *args):
    config_path = tmp_path / "bench.json"
    config_path.write_text(json.dumps(config(**settings)))
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
            "build.py": "from pathlib import Path; Path('build.txt').write_text('expected\\n')"
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
    (tmp_path / "history.jsonl").write_text(json.dumps(history[0]) + "\n")
    result = cli(repository, tmp_path, settings, "--compare", "history")
    assert result.returncode == 1
    report = json.loads((tmp_path / "report.json").read_text())
    assert report["artifacts"][0]["regression"]
    assert len(bench.read_history(tmp_path / "history.jsonl")) == 2
    assert "REGRESSION" in (tmp_path / "report.html").read_text()


def test_cli_rejects_in_repo_outputs(repository, tmp_path):
    commit_fixture(repository, {"build.py": "pass"})
    settings = tmp_path / "bench.json"
    settings.write_text(json.dumps(config()))
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
    assert "synthetic-sensitive-output" not in (tmp_path / "report.json").read_text()


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
    settings.write_text(json.dumps(config()))
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
            "build.py": "from pathlib import Path; Path('build.txt').write_text('expected\\n')"
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
