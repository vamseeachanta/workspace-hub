from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


def load_local_ci():
    script = Path(__file__).resolve().parents[3] / "scripts" / "ci" / "local-ci" / "local-ci.py"
    spec = importlib.util.spec_from_file_location("local_ci_script", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_workflow(repo: Path) -> None:
    workflow_dir = repo / ".github" / "workflows"
    workflow_dir.mkdir(parents=True)
    (workflow_dir / "ci.yml").write_text(
        """
name: CI
on:
  pull_request:
  schedule:
    - cron: "0 0 * * *"
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: echo "TOKEN=$SECRET_TOKEN" && echo ok
      - uses: unknown/action@v1
      - run: exit 0
  mac:
    runs-on: macos-latest
    steps:
      - run: echo ignored
""",
        encoding="utf-8",
    )


class FakeRunner:
    def __init__(self, module, repo_path: Path) -> None:
        self.module = module
        self.repo_path = repo_path
        self.repo_path.mkdir(parents=True, exist_ok=True)
        self.calls: list[list[str]] = []
        self.statuses: list[dict[str, str]] = []
        self.comments: list[str] = []

    def __call__(self, cmd, **kwargs):
        args = [str(part) for part in cmd]
        self.calls.append(args)
        if args[:3] == ["gh", "pr", "list"]:
            repo = args[args.index("--repo") + 1]
            sha = "missing123" if repo.endswith("/missing") else "abc123"
            return self.module.CommandResult(
                0,
                json.dumps(
                    [
                        {
                            "number": 7,
                            "headRefOid": sha,
                            "url": "https://example.invalid/pr/7",
                        }
                    ]
                ),
                "",
            )
        if args[:6] == ["git", "-C", str(self.repo_path), "worktree", "add", "--detach"]:
            worktree = Path(args[6])
            write_workflow(worktree)
            return self.module.CommandResult(0, "", "")
        if args[:6] == ["git", "-C", str(self.repo_path), "worktree", "remove", "--force"]:
            return self.module.CommandResult(0, "", "")
        if args[:5] == ["git", "-C", str(self.repo_path), "worktree", "prune"]:
            return self.module.CommandResult(0, "", "")
        if args[:4] == ["git", "worktree", "add", "--detach"]:
            raise AssertionError("worktree add must use git -C <repo_path>")
        if args[:3] == ["git", "worktree", "remove"]:
            raise AssertionError("worktree remove must use git -C <repo_path>")
        if args[:3] == ["git", "-C", str(self.repo_path)]:
            return self.module.CommandResult(0, "", "")
        if args[:2] == ["gh", "api"] and args[2].endswith("/issues/7/comments"):
            return self.module.CommandResult(0, "[]", "")
        if args[:2] == ["gh", "api"] and args[2].startswith("repos/"):
            fields = {}
            for idx, arg in enumerate(args):
                if arg == "-f":
                    key, value = args[idx + 1].split("=", 1)
                    fields[key] = value
            self.statuses.append(fields)
            return self.module.CommandResult(0, "", "")
        if args[:3] == ["gh", "pr", "comment"]:
            body_file = Path(args[args.index("--body-file") + 1])
            self.comments.append(body_file.read_text(encoding="utf-8"))
            return self.module.CommandResult(0, "", "")
        if args[0] == "bash":
            run_input = kwargs.get("input_text", "")
            stdout = run_input.replace("$SECRET_TOKEN", "super-secret-value")
            return self.module.CommandResult(0, stdout, "")
        raise AssertionError(f"unexpected command: {args}")


def test_runs_pull_request_ubuntu_jobs_posts_status_comment_and_state(tmp_path, monkeypatch):
    module = load_local_ci()
    monkeypatch.setenv("SECRET_TOKEN", "super-secret-value")
    monkeypatch.delenv("LOCAL_CI_COMMENT", raising=False)
    repo_path = tmp_path / "repos" / "owner" / "sample"
    runner = FakeRunner(module, repo_path)
    config = {
        "owner": "owner",
        "repo_root": str(tmp_path / "repos"),
        "worktree_root": str(tmp_path / "worktrees"),
        "state_dir": str(tmp_path / "state"),
        "job_timeout_seconds": 20,
        "repos": [{"name": "sample"}],
    }

    result = module.run_once(config, runner=runner)

    assert result == 0
    contexts = [status["context"] for status in runner.statuses]
    assert "local-ci/CI/test" in contexts
    assert all("mac" not in context for context in contexts)
    descriptions = [status["description"] for status in runner.statuses]
    assert any("skipped-step: unknown/action@v1" in description for description in descriptions)
    assert not runner.comments
    log_path = tmp_path / "state" / "logs" / "owner__sample" / "abc123__local-ci_CI_test.log"
    assert log_path.exists()
    assert "super-secret-value" not in log_path.read_text(encoding="utf-8")
    state = json.loads((tmp_path / "state" / "state.json").read_text(encoding="utf-8"))
    assert state["repos"]["owner/sample"]["last_heads"] == ["abc123"]
    assert any(call[:6] == ["git", "-C", str(repo_path), "worktree", "add", "--detach"] for call in runner.calls)
    assert any(call[:5] == ["git", "-C", str(repo_path), "worktree", "prune"] for call in runner.calls)


def test_seen_sha_is_not_rerun(tmp_path):
    module = load_local_ci()
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    (state_dir / "state.json").write_text(
        json.dumps({"repos": {"owner/sample": {"last_heads": ["abc123"], "comments": {}}}}),
        encoding="utf-8",
    )
    runner = FakeRunner(module, tmp_path / "repos" / "owner" / "sample")
    config = {
        "owner": "owner",
        "repo_root": str(tmp_path / "repos"),
        "worktree_root": str(tmp_path / "worktrees"),
        "state_dir": str(state_dir),
        "repos": [{"name": "sample"}],
    }

    result = module.run_once(config, runner=runner)

    assert result == 0
    assert not any(call[:3] == ["git", "worktree", "add"] for call in runner.calls)
    assert not runner.statuses


def test_missing_checkout_does_not_stop_second_repo(tmp_path, monkeypatch):
    module = load_local_ci()
    monkeypatch.delenv("LOCAL_CI_COMMENT", raising=False)
    repo_path = tmp_path / "repos" / "owner" / "sample"
    runner = FakeRunner(module, repo_path)
    config = {
        "owner": "owner",
        "repo_root": str(tmp_path / "repos"),
        "worktree_root": str(tmp_path / "worktrees"),
        "state_dir": str(tmp_path / "state"),
        "job_timeout_seconds": 20,
        "repos": [{"name": "missing"}, {"name": "sample"}],
    }

    result = module.run_once(config, runner=runner)

    assert result == 2
    contexts = [status["context"] for status in runner.statuses]
    assert "local-ci/runner" in contexts
    assert "local-ci/CI/test" in contexts
    state = json.loads((tmp_path / "state" / "state.json").read_text(encoding="utf-8"))
    assert state["repos"]["owner/missing"]["last_heads"] == ["missing123"]
    assert state["repos"]["owner/sample"]["last_heads"] == ["abc123"]


def test_timeout_becomes_failure(tmp_path):
    module = load_local_ci()

    def timeout_runner(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout"), output="partial")

    result = module.run_shell_step("sleep 10", tmp_path, 1, runner=timeout_runner, env={})

    assert result.returncode == 124
    assert result.stdout == "partial"
    assert result.stderr == "timeout"


def test_expression_step_is_skipped(tmp_path):
    module = load_local_ci()
    calls = []

    def runner(cmd, **kwargs):
        calls.append(cmd)
        return module.CommandResult(0, "", "")

    result = module.run_job(
        {"steps": [{"name": "guarded", "run": "echo ${{ github.ref }}"}, {"name": "plain", "run": "echo ok"}]},
        tmp_path,
        20,
        runner=runner,
    )

    assert result.state == "success"
    assert result.description == "ok (1 skipped: skipped-step: expression in guarded)"
    assert len(calls) == 1


def test_matrix_job_is_skipped(tmp_path):
    module = load_local_ci()

    result = module.run_job(
        {"strategy": {"matrix": {"python": ["3.11", "3.12"]}}, "steps": [{"run": "exit 1"}]},
        tmp_path,
        20,
        runner=lambda cmd, **kwargs: module.CommandResult(1, "", "should not run"),
    )

    assert result.state == "success"
    assert result.description == "skipped: matrix job not supported locally"


def test_last_heads_are_capped_at_200():
    module = load_local_ci()
    state = {"repos": {}}

    for index in range(205):
        module.remember_head(state, "owner", "sample", f"sha{index}")

    heads = state["repos"]["owner/sample"]["last_heads"]
    assert len(heads) == 200
    assert heads[0] == "sha5"
    assert heads[-1] == "sha204"
