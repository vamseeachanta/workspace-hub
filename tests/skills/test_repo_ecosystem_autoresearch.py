"""Regression tests for the repo ecosystem autoresearch runner (#2417)."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "scripts" / "skills" / "repo_ecosystem_autoresearch.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("repo_ecosystem_autoresearch", RUNNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_fixture_tree(root: Path) -> None:
    (root / ".claude" / "skills" / "alpha").mkdir(parents=True)
    (root / ".claude" / "skills" / "beta").mkdir(parents=True)
    (root / ".claude" / "skills" / "alpha" / "SKILL.md").write_text(
        "---\nname: alpha\n---\n# Alpha\n", encoding="utf-8"
    )
    (root / ".claude" / "skills" / "beta" / "SKILL.md").write_text(
        "---\nname: beta\n---\n# Beta\n", encoding="utf-8"
    )

    (root / ".claude" / "agents").mkdir(parents=True)
    (root / ".claude" / "agents" / "reviewer.md").write_text(
        "---\nname: reviewer\n---\n# Reviewer\n", encoding="utf-8"
    )

    (root / ".claude" / "get-shit-done" / "templates").mkdir(parents=True)
    (root / ".claude" / "get-shit-done" / "templates" / "plan.md").write_text(
        "# Plan\n{{goal}}\n", encoding="utf-8"
    )

    (root / "config" / "scheduled-tasks").mkdir(parents=True)
    (root / "config" / "scheduled-tasks" / "schedule-tasks.yaml").write_text(
        "tasks: []\n", encoding="utf-8"
    )


def test_discovers_supported_target_types(tmp_path: Path) -> None:
    runner = load_runner()
    write_fixture_tree(tmp_path)

    assert [target.path.relative_to(tmp_path).as_posix() for target in runner.discover_targets(tmp_path, "skill")] == [
        ".claude/skills/alpha/SKILL.md",
        ".claude/skills/beta/SKILL.md",
    ]
    assert [target.path.relative_to(tmp_path).as_posix() for target in runner.discover_targets(tmp_path, "agent")] == [
        ".claude/agents/reviewer.md",
    ]
    assert [target.path.relative_to(tmp_path).as_posix() for target in runner.discover_targets(tmp_path, "template")] == [
        ".claude/get-shit-done/templates/plan.md",
    ]
    assert [
        target.path.relative_to(tmp_path).as_posix()
        for target in runner.discover_targets(tmp_path, "workflow-config")
    ] == ["config/scheduled-tasks/schedule-tasks.yaml"]


def test_target_type_dispatches_to_registered_evaluator(tmp_path: Path) -> None:
    runner = load_runner()
    target = runner.Target("agent", tmp_path / ".claude" / "agents" / "reviewer.md")
    target.path.parent.mkdir(parents=True)
    target.path.write_text("# Reviewer\nTODO\n", encoding="utf-8")
    calls: list[str] = []

    def evaluator(path: Path) -> runner.Evaluation:
        calls.append(path.name)
        return runner.Evaluation(warnings=1, criticals=0, findings=["todo"])

    result = runner.evaluate_target(target, {"agent": evaluator})

    assert calls == ["reviewer.md"]
    assert result.warnings == 1
    assert result.findings == ["todo"]


def test_skill_evaluator_uses_one_full_baseline_for_candidate_ranking(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    write_fixture_tree(tmp_path)
    eval_script = tmp_path / "eval-skills.py"
    eval_script.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    calls: list[list[str]] = []

    class FakeProcess:
        returncode = 1
        stderr = ""
        stdout = json.dumps(
            {
                "results": [
                    {"name": "alpha", "issues": [{"severity": "WARNING", "message": "alpha warning"}]},
                    {"name": "beta", "issues": [{"severity": "WARNING", "message": "beta warning"}]},
                ]
            }
        )

    def fake_run(args, **_kwargs) -> FakeProcess:
        calls.append(args)
        return FakeProcess()

    monkeypatch.setattr(runner.subprocess, "run", fake_run)
    evaluator = runner.make_skill_evaluator(tmp_path, eval_script)

    assert evaluator(tmp_path / ".claude" / "skills" / "alpha" / "SKILL.md").warnings == 1
    assert evaluator(tmp_path / ".claude" / "skills" / "beta" / "SKILL.md").warnings == 1

    assert len(calls) == 1
    assert calls[0][-2:] == ["--format", "json"]


def test_revert_on_non_improvement_records_generalized_result(tmp_path: Path) -> None:
    runner = load_runner()
    target = runner.Target("template", tmp_path / ".claude" / "get-shit-done" / "templates" / "plan.md")
    target.path.parent.mkdir(parents=True)
    target.path.write_text("needs context\n", encoding="utf-8")
    results_file = tmp_path / "results.jsonl"
    evaluations = iter(
        [
            runner.Evaluation(warnings=1, criticals=0, findings=["missing explicit placeholders"]),
            runner.Evaluation(warnings=1, criticals=0, findings=["still missing explicit placeholders"]),
        ]
    )

    outcome = runner.run_attempt(
        target,
        evaluator=lambda _path: next(evaluations),
        candidate_provider=lambda _target, _before: "still needs context\n",
        results_file=results_file,
        commit_callback=None,
        dry_run=False,
    )

    assert outcome.result == "revert-no-improve"
    assert target.path.read_text(encoding="utf-8") == "needs context\n"
    row = json.loads(results_file.read_text(encoding="utf-8"))
    assert row["target_type"] == "template"
    assert row["target_path"] == ".claude/get-shit-done/templates/plan.md"
    assert row["warnings_before"] == 1
    assert row["warnings_after"] == 1


def test_keep_on_improvement_can_call_branch_isolated_commit(tmp_path: Path) -> None:
    runner = load_runner()
    target = runner.Target("agent", tmp_path / ".claude" / "agents" / "reviewer.md")
    target.path.parent.mkdir(parents=True)
    target.path.write_text("TODO\n", encoding="utf-8")
    results_file = tmp_path / "results.jsonl"
    evaluations = iter(
        [
            runner.Evaluation(warnings=1, criticals=0, findings=["todo"]),
            runner.Evaluation(warnings=0, criticals=0, findings=[]),
        ]
    )
    committed: list[Path] = []

    outcome = runner.run_attempt(
        target,
        evaluator=lambda _path: next(evaluations),
        candidate_provider=lambda _target, _before: "Ready\n",
        results_file=results_file,
        commit_callback=lambda path, _message: committed.append(path),
        dry_run=False,
    )

    assert outcome.result == "kept"
    assert target.path.read_text(encoding="utf-8") == "Ready\n"
    assert committed == [target.path]
    row = json.loads(results_file.read_text(encoding="utf-8"))
    assert row["target_type"] == "agent"
    assert row["target_path"] == ".claude/agents/reviewer.md"
    assert row["warnings_after"] == 0


def test_prepare_branch_isolates_work_on_autoresearch_branch(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    calls: list[list[str]] = []

    class FakeProcess:
        def __init__(self, returncode: int = 0, stdout: str = ""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = ""

    def fake_run_git(_root: Path, args: list[str], check: bool = True) -> FakeProcess:
        calls.append(args)
        if args == ["branch", "--show-current"]:
            return FakeProcess(stdout="codex/nextwave-20260427-issue-2417\n")
        if args == ["status", "--porcelain"]:
            return FakeProcess(stdout="")
        if args == ["rev-parse", "--verify", "autoresearch/repo-ecosystem-2026-04-27"]:
            return FakeProcess(returncode=1)
        if args == ["switch", "-c", "autoresearch/repo-ecosystem-2026-04-27", "main"]:
            return FakeProcess(returncode=0)
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(runner, "run_git", fake_run_git)

    original, stashed = runner.prepare_branch(tmp_path, "autoresearch/repo-ecosystem-2026-04-27")

    assert original == "codex/nextwave-20260427-issue-2417"
    assert stashed is False
    assert ["switch", "-c", "autoresearch/repo-ecosystem-2026-04-27", "main"] in calls


def test_prepare_branch_does_not_mark_stash_when_stash_push_fails(tmp_path: Path, monkeypatch) -> None:
    runner = load_runner()
    calls: list[list[str]] = []

    class FakeProcess:
        def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

    def fake_run_git(_root: Path, args: list[str], check: bool = True) -> FakeProcess:
        calls.append(args)
        if args == ["branch", "--show-current"]:
            return FakeProcess(stdout="codex/nextwave-20260427-issue-2417\n")
        if args == ["status", "--porcelain"]:
            return FakeProcess(stdout=" M docs/notes.md\n")
        if args[:4] == ["stash", "push", "--include-untracked", "-m"]:
            return FakeProcess(returncode=1, stderr="cannot save the current worktree state")
        if args == ["rev-parse", "--verify", "autoresearch/repo-ecosystem-2026-04-27"]:
            return FakeProcess(returncode=1)
        if args == ["switch", "-c", "autoresearch/repo-ecosystem-2026-04-27", "main"]:
            return FakeProcess(returncode=0)
        if args == ["switch", "codex/nextwave-20260427-issue-2417"]:
            return FakeProcess(returncode=0)
        if args == ["stash", "pop"]:
            return FakeProcess(returncode=0)
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(runner, "run_git", fake_run_git)

    original, stashed = runner.prepare_branch(tmp_path, "autoresearch/repo-ecosystem-2026-04-27")
    runner.restore_branch(tmp_path, original, stashed)

    assert original == "codex/nextwave-20260427-issue-2417"
    assert stashed is False
    assert ["stash", "pop"] not in calls


def test_cli_dry_run_supports_every_v1_target_type(tmp_path: Path, capsys) -> None:
    runner = load_runner()
    write_fixture_tree(tmp_path)

    for target_type in ["skill", "agent", "template", "workflow-config"]:
        assert (
            runner.main(
                [
                    "--root",
                    str(tmp_path),
                    "--target-type",
                    target_type,
                    "--dry-run",
                    "--max-attempts",
                    "1",
                ]
            )
            == 0
        )

    output = capsys.readouterr().out
    assert "Dry run" in output
    assert "workflow-config" in output
