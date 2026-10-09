from __future__ import annotations

import importlib.util
import json
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
            return self.module.CommandResult(
                0,
                json.dumps(
                    [
                        {
                            "number": 7,
                            "headRefOid": "abc123",
                            "url": "https://example.invalid/pr/7",
                        }
                    ]
                ),
                "",
            )
        if args[:3] == ["git", "-C", str(self.repo_path)]:
            return self.module.CommandResult(0, "", "")
        if args[:4] == ["git", "worktree", "add", "--detach"]:
            worktree = Path(args[4])
            write_workflow(worktree)
            return self.module.CommandResult(0, "", "")
        if args[:3] == ["git", "worktree", "remove"]:
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
    assert runner.comments
    assert "super-secret-value" not in runner.comments[-1]
    state = json.loads((tmp_path / "state" / "state.json").read_text(encoding="utf-8"))
    assert state["repos"]["owner/sample"]["last_heads"] == ["abc123"]


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
