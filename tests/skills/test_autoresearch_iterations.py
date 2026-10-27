"""Synthetic controller cases for issue #2418.

Policy: issue #2418 requests opt-in iteration and bounded stopping; the
bounded task specification narrows the default to one.
All other numbers below are synthetic inputs or hand-counted expectations:
each candidate is one attempt, each strict improvement is one keep, and each
rejected evaluation is one revert. Clock values are synthetic seconds.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def runner(monkeypatch):
    path = Path(__file__).resolve().parents[2] / "scripts/skills/repo_ecosystem_autoresearch.py"
    spec = importlib.util.spec_from_file_location("iteration_runner", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def forbidden_process(*_args, **_kwargs):
        raise AssertionError("controller tests must not invoke external processes")

    monkeypatch.setattr(module.subprocess, "run", forbidden_process)
    return module


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


@pytest.fixture
def scenario(runner, tmp_path):
    def build(candidates, *, scores=None, duration=0.0):
        target = runner.Target("template", tmp_path / "target.txt", tmp_path)
        target.path.write_text("baseline", encoding="utf-8")
        # Independent score table: two improvements, plateau, warning regression,
        # and a critical regression even though its warning count is lower.
        evaluations = scores or {
            "baseline": (3, 0),
            "better": (2, 0),
            "best": (1, 0),
            "plateau": (2, 0),
            "worse": (4, 0),
            "critical": (0, 1),
        }
        clock = FakeClock()
        pending = iter(candidates)
        seen = []
        commits = []

        def evaluate(path):
            warnings, criticals = evaluations[path.read_text(encoding="utf-8")]
            return runner.Evaluation(warnings, criticals)

        def propose(current, before):
            seen.append((current.path.read_text(encoding="utf-8"), before.warnings))
            clock.now += duration
            return next(pending)

        kwargs = dict(
            target=target,
            evaluator=evaluate,
            candidate_provider=propose,
            results_file=tmp_path / "results.jsonl",
            commit_callback=lambda path, _message: commits.append(path.read_text(encoding="utf-8")),
            dry_run=False,
            clock=clock,
        )
        return SimpleNamespace(kwargs=kwargs, target=target, seen=seen, commits=commits, clock=clock)

    return build


def counts(summary):
    return summary.attempted, summary.kept, summary.reverted


def test_default_mode_makes_one_attempt(runner, scenario):
    case = scenario(["better", "best"])
    summary = runner.run_iterations(**case.kwargs)
    # One proposal, one keep, no revert; the unused second proposal stays unused.
    assert counts(summary) == (1, 1, 0)
    assert summary.stop_reason == "attempt-cap"
    assert case.seen == [("baseline", 3)]
    assert case.commits == ["better"]


def test_stops_on_no_improvement(runner, scenario):
    case = scenario(["better", "plateau", "best"])
    summary = runner.run_iterations(**case.kwargs, iterations=3)
    # Baseline 3 -> 2 is kept; 2 -> 2 is reverted and the third is not tried.
    assert counts(summary) == (2, 1, 1)
    assert summary.stop_reason == "no-improvement"
    assert case.target.path.read_text(encoding="utf-8") == "better"
    assert case.seen == [("baseline", 3), ("better", 2)]
    assert case.commits == ["better"]


@pytest.mark.parametrize("regression", ["worse", "critical"])
def test_regression_restores_last_kept_content(runner, scenario, regression):
    case = scenario(["better", regression, "best"])
    summary = runner.run_iterations(**case.kwargs, iterations=3)
    # One accepted candidate followed by one rejected candidate restores "better".
    assert counts(summary) == (2, 1, 1)
    assert summary.stop_reason == "regression"
    assert case.target.path.read_text(encoding="utf-8") == "better"
    assert case.commits == ["better"]
    assert len(case.seen) == 2


def test_compounds_until_configured_attempt_cap(runner, scenario):
    case = scenario(["better", "best"])
    summary = runner.run_iterations(**case.kwargs, iterations=2)
    # Two strictly improving proposals: 3 -> 2 -> 1, two keeps and no revert.
    assert counts(summary) == (2, 2, 0)
    assert summary.stop_reason == "attempt-cap"
    assert case.seen == [("baseline", 3), ("better", 2)]
    assert case.commits == ["better", "best"]


@pytest.mark.parametrize("duration", [5.0, 6.0])
def test_elapsed_budget_stops_before_next_attempt(runner, scenario, duration):
    case = scenario(["better", "best"], duration=duration)
    summary = runner.run_iterations(**case.kwargs, iterations=3, time_budget=5.0)
    # First attempt consumes at least the five-second allowance; no second starts.
    assert counts(summary) == (1, 1, 0)
    assert summary.stop_reason == "elapsed-budget"
    assert summary.elapsed_s == duration
    assert len(case.seen) == 1


def test_elapsed_budget_allows_attempt_before_boundary(runner, scenario):
    case = scenario(["better", "best"], duration=2.0)
    summary = runner.run_iterations(**case.kwargs, iterations=2, time_budget=5.0)
    # Attempts start at zero and two seconds, finish at four: both fit admission.
    assert counts(summary) == (2, 2, 0)
    assert summary.elapsed_s == 4.0
    assert summary.stop_reason == "attempt-cap"


def test_zero_budget_does_not_start_attempt(runner, scenario):
    case = scenario(["better"])
    summary = runner.run_iterations(**case.kwargs, time_budget=0)
    assert counts(summary) == (0, 0, 0)
    assert summary.stop_reason == "elapsed-budget"
    assert case.seen == []
    assert not case.kwargs["results_file"].exists()


def test_unavailable_candidate_is_not_counted_as_reverted(runner, scenario):
    case = scenario([])

    def unavailable(_target, _before):
        raise runner.CandidateUnavailable("synthetic unavailable candidate")

    case.kwargs["candidate_provider"] = unavailable
    summary = runner.run_iterations(**case.kwargs, iterations=3)
    assert counts(summary) == (1, 0, 0)
    assert summary.stop_reason == "no-candidate"
    assert case.target.path.read_text(encoding="utf-8") == "baseline"
    assert case.commits == []


def test_dry_run_stops_without_requesting_candidates(runner, scenario):
    case = scenario([])
    case.kwargs["dry_run"] = True
    summary = runner.run_iterations(**case.kwargs, iterations=3)
    assert counts(summary) == (1, 0, 0)
    assert summary.stop_reason == "dry-run"
    assert case.seen == []
    assert case.commits == []


@pytest.mark.parametrize("iterations", [0, -1, 1.5, True])
def test_invalid_attempt_cap_is_rejected_before_work(runner, scenario, iterations):
    case = scenario([])
    with pytest.raises(ValueError, match="iterations"):
        runner.run_iterations(**case.kwargs, iterations=iterations)
    assert case.seen == []


@pytest.mark.parametrize("budget", [-1, float("nan"), float("inf")])
def test_invalid_elapsed_budget_is_rejected_before_work(runner, scenario, budget):
    case = scenario([])
    with pytest.raises(ValueError, match="time_budget"):
        runner.run_iterations(**case.kwargs, time_budget=budget)
    assert case.seen == []


@pytest.mark.parametrize("arguments", [["--iterations", "0"], ["--time-budget", "-1"]])
def test_cli_rejects_invalid_bounds(runner, arguments):
    with pytest.raises(SystemExit) as error:
        runner.parse_args(arguments)
    assert error.value.code == 2  # argparse's documented invalid-argument exit.


@pytest.mark.parametrize("arguments, expected", [([], 1), (["--iterations", "2"], 2)])
def test_cli_runs_bounded_controller(runner, scenario, monkeypatch, capsys, arguments, expected):
    case = scenario(["better", "best"])
    root = case.target.path.parent
    monkeypatch.setattr(runner, "default_evaluators", lambda *_args: {"template": case.kwargs["evaluator"]})
    monkeypatch.setattr(runner, "discover_targets", lambda *_args: [case.target])
    monkeypatch.setattr(runner, "default_candidate_provider", lambda target, before, **_kw: case.kwargs["candidate_provider"](target, before))
    monkeypatch.setattr(runner, "make_git_safe_commit_callback", lambda _root: case.kwargs["commit_callback"])
    monkeypatch.setattr(runner.time, "monotonic", case.clock)

    assert runner.main([
        "--root", str(root), "--target-type", "template", "--no-branch",
        "--results-file", str(case.kwargs["results_file"]), *arguments,
    ]) == 0

    output = capsys.readouterr().out.splitlines()
    summary = json.loads(next(line for line in output if line.startswith("{")))
    assert summary["attempted"] == expected
    assert summary["kept"] == expected
    assert summary["reverted"] == 0
    assert summary["stop_reason"] == "attempt-cap"
    # Existing per-attempt JSONL schema remains one row per actual attempt.
    rows = [json.loads(line) for line in case.kwargs["results_file"].read_text(encoding="utf-8").splitlines()]
    assert len(rows) == expected
    assert all(row["result"] == "kept" for row in rows)
