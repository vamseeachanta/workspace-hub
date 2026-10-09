#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG = Path(__file__).with_name("repos.yaml")
DEFAULT_STATE_DIR = Path.home() / ".local" / "state" / "local-ci"
DEFAULT_REPO_ROOT = Path.home() / "ws"
DEFAULT_WORKTREE_ROOT = Path.home() / ".local" / "tmp" / "local-ci" / "worktrees"
COMMENT_MARKER = "<!-- local-ci:managed -->"
MAX_DESCRIPTION = 140
LOG_TAIL_LINES = 50


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


@dataclass
class JobResult:
    state: str
    description: str
    log: str


def run_command(cmd: list[str], **kwargs: Any) -> CommandResult:
    completed = subprocess.run(
        cmd,
        cwd=kwargs.get("cwd"),
        input=kwargs.get("input_text"),
        text=True,
        capture_output=True,
        timeout=kwargs.get("timeout"),
        env=kwargs.get("env"),
        check=False,
    )
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def load_config(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    config.setdefault("state_dir", str(DEFAULT_STATE_DIR))
    config.setdefault("repo_root", str(DEFAULT_REPO_ROOT))
    config.setdefault("worktree_root", str(DEFAULT_WORKTREE_ROOT))
    config.setdefault("job_timeout_seconds", 900)
    config.setdefault("owner", "vamseeachanta")
    return config


def load_state(state_dir: Path) -> dict[str, Any]:
    state_path = state_dir / "state.json"
    if not state_path.exists():
        return {"repos": {}}
    with state_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state_dir: Path, state: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    target = state_dir / "state.json"
    tmp = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(target)


def gh_prs(owner: str, repo: str, runner=run_command) -> list[dict[str, Any]]:
    result = runner(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            f"{owner}/{repo}",
            "--state",
            "open",
            "--json",
            "number,headRefOid,url",
        ]
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh pr list failed for {owner}/{repo}: {result.stderr.strip()}")
    return json.loads(result.stdout or "[]")


def resolve_repo_path(config: dict[str, Any], repo_cfg: dict[str, Any]) -> Path:
    if repo_cfg.get("path"):
        return Path(repo_cfg["path"]).expanduser()
    owner = repo_cfg.get("owner") or config["owner"]
    return Path(config["repo_root"]).expanduser() / owner / repo_cfg["name"]


def prepare_repo(owner: str, repo: str, repo_path: Path, runner=run_command) -> Path:
    if not repo_path.exists():
        raise RuntimeError(f"configured checkout does not exist for {owner}/{repo}: {repo_path}")
    result = runner(["git", "-C", str(repo_path), "fetch", "--prune", "origin"])
    if result.returncode != 0:
        raise RuntimeError(f"git fetch failed for {owner}/{repo}: {result.stderr.strip()}")
    return repo_path


def create_worktree(repo_path: Path, sha: str, root: Path, runner=run_command) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{repo_path.parent.name}-{repo_path.name}-{sha[:12]}-{int(time.time())}"
    result = runner(["git", "worktree", "add", "--detach", str(path), sha])
    if result.returncode != 0:
        raise RuntimeError(f"git worktree add failed for {sha}: {result.stderr.strip()}")
    return path


def fetch_pr_head(repo_path: Path, pr_number: int, runner=run_command) -> None:
    result = runner(["git", "-C", str(repo_path), "fetch", "origin", f"refs/pull/{pr_number}/head"])
    if result.returncode != 0:
        raise RuntimeError(f"git fetch failed for PR {pr_number}: {result.stderr.strip()}")


def remove_worktree(path: Path, runner=run_command) -> None:
    result = runner(["git", "worktree", "remove", "--force", str(path)])
    if result.returncode != 0 and path.exists():
        shutil.rmtree(path, ignore_errors=True)


def workflow_triggers_pull_request(workflow: dict[str, Any]) -> bool:
    trigger = workflow.get("on", workflow.get(True))
    if trigger == "pull_request":
        return True
    if isinstance(trigger, list):
        return "pull_request" in trigger
    if isinstance(trigger, dict):
        return "pull_request" in trigger
    return False


def workflow_is_out_of_scope(workflow: dict[str, Any]) -> bool:
    trigger = workflow.get("on", workflow.get(True))
    if isinstance(trigger, dict) and "pages" in trigger and "pull_request" not in trigger:
        return True
    return not workflow_triggers_pull_request(workflow)


def ubuntu_job(job: dict[str, Any]) -> bool:
    runs_on = job.get("runs-on")
    values = runs_on if isinstance(runs_on, list) else [runs_on]
    return any(isinstance(value, str) and value.startswith("ubuntu-") for value in values)


def find_jobs(worktree: Path) -> list[tuple[str, str, dict[str, Any]]]:
    jobs: list[tuple[str, str, dict[str, Any]]] = []
    for workflow_path in sorted((worktree / ".github" / "workflows").glob("*.y*ml")):
        with workflow_path.open(encoding="utf-8") as handle:
            workflow = yaml.safe_load(handle) or {}
        if workflow_is_out_of_scope(workflow):
            continue
        workflow_name = str(workflow.get("name") or workflow_path.stem)
        for job_name, job in (workflow.get("jobs") or {}).items():
            if isinstance(job, dict) and ubuntu_job(job):
                jobs.append((workflow_name, str(job_name), job))
    return jobs


def shim_uses(uses: str) -> tuple[str, str | None]:
    action = uses.split("@", 1)[0].lower()
    if action == "actions/checkout":
        return "ok", "actions/checkout: already checked out"
    if action in {"actions/setup-python", "astral-sh/setup-uv", "actions/setup-node"}:
        return "ok", f"{action}: using host toolchain"
    if action in {"davidanson/markdownlint-cli2-action", "nosborn/github-action-markdown-cli"}:
        return "run", "npx markdownlint-cli2"
    if action in {"lycheeverse/lychee-action"}:
        return "run", "lychee ."
    return "skipped", f"skipped-step: {uses}"


def redaction_values() -> list[str]:
    values = []
    for value in os.environ.values():
        if not value or len(value) < 4:
            continue
        values.append(value)
    return sorted(set(values), key=len, reverse=True)


def redact(text: str, secrets: list[str]) -> str:
    redacted = text
    for secret in secrets:
        redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


def safe_env() -> dict[str, str]:
    allowed = {"HOME", "PATH", "LANG", "LC_ALL", "TMPDIR", "UV_CACHE_DIR"}
    return {key: value for key, value in os.environ.items() if key in allowed}


def run_shell_step(script: str, worktree: Path, timeout: int, runner=run_command) -> CommandResult:
    return runner(["bash", "-e"], cwd=str(worktree), input_text=script, timeout=timeout, env=safe_env())


def run_job(job: dict[str, Any], worktree: Path, timeout: int, runner=run_command) -> JobResult:
    log_parts: list[str] = []
    skipped: list[str] = []
    secrets = redaction_values()
    deadline = time.monotonic() + timeout
    for index, step in enumerate(job.get("steps") or [], start=1):
        raw_remaining = deadline - time.monotonic()
        if raw_remaining <= 0:
            log_parts.append("job timeout exceeded\n")
            return finish_job("failure", skipped, log_parts, secrets)
        remaining = max(1, int(raw_remaining))
        if not isinstance(step, dict):
            continue
        label = str(step.get("name") or step.get("uses") or f"run step {index}")
        if "uses" in step:
            state, command = shim_uses(str(step["uses"]))
            log_parts.append(f"$ {label}\n{command or ''}\n")
            if state == "skipped":
                skipped.append(command or str(step["uses"]))
            elif state == "run" and command:
                result = run_shell_step(command, worktree, remaining, runner)
                log_parts.append(result.stdout + result.stderr)
                if result.returncode != 0:
                    return finish_job("failure", skipped, log_parts, secrets)
            continue
        if "run" in step:
            log_parts.append(f"$ {label}\n")
            result = run_shell_step(str(step["run"]), worktree, remaining, runner)
            log_parts.append(result.stdout + result.stderr)
            if result.returncode != 0:
                return finish_job("failure", skipped, log_parts, secrets)
    return finish_job("success", skipped, log_parts, secrets)


def finish_job(state: str, skipped: list[str], log_parts: list[str], secrets: list[str]) -> JobResult:
    description = "ok" if state == "success" else "job failed"
    if skipped:
        description = skipped[0]
    description = description[:MAX_DESCRIPTION]
    log = redact("".join(log_parts), secrets)
    return JobResult(state, description, log)


def post_status(
    owner: str,
    repo: str,
    sha: str,
    context: str,
    state: str,
    description: str,
    runner=run_command,
    target_url: str | None = None,
) -> None:
    args = [
        "gh",
        "api",
        f"repos/{owner}/{repo}/statuses/{sha}",
        "-f",
        f"state={state}",
        "-f",
        f"context={context}",
        "-f",
        f"description={description[:MAX_DESCRIPTION]}",
    ]
    if target_url:
        args.extend(["-f", f"target_url={target_url}"])
    result = runner(args)
    if result.returncode != 0:
        raise RuntimeError(f"status post failed for {context}: {result.stderr.strip()}")


def find_managed_comment(owner: str, repo: str, pr_number: int, runner=run_command) -> int | None:
    result = runner(["gh", "api", f"repos/{owner}/{repo}/issues/{pr_number}/comments", "--paginate"])
    if result.returncode != 0:
        return None
    comments = json.loads(result.stdout or "[]")
    for comment in comments:
        if COMMENT_MARKER in str(comment.get("body", "")):
            return int(comment["id"])
    return None


def post_comment(owner: str, repo: str, pr_number: int, body: str, runner=run_command) -> None:
    comment_id = find_managed_comment(owner, repo, pr_number, runner)
    if comment_id is not None:
        result = runner(["gh", "api", f"repos/{owner}/{repo}/issues/comments/{comment_id}", "-X", "PATCH", "-f", f"body={body}"])
        if result.returncode != 0:
            raise RuntimeError(f"PR comment update failed for {owner}/{repo}#{pr_number}: {result.stderr.strip()}")
        return
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(body)
        body_path = Path(handle.name)
    try:
        result = runner(["gh", "pr", "comment", str(pr_number), "--repo", f"{owner}/{repo}", "--body-file", str(body_path)])
        if result.returncode != 0:
            raise RuntimeError(f"PR comment failed for {owner}/{repo}#{pr_number}: {result.stderr.strip()}")
    finally:
        body_path.unlink(missing_ok=True)


def create_log_gist(context: str, log: str, runner=run_command) -> str | None:
    result = runner(
        ["gh", "gist", "create", "--private", "--filename", "local-ci.log", "--desc", context, "-"],
        input_text=log,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip().splitlines()[-1] if result.stdout.strip() else None


def build_comment(repo: str, sha: str, results: list[tuple[str, JobResult]]) -> str:
    lines = [COMMENT_MARKER, f"local-ci run for `{repo}` at `{sha}`", ""]
    for context, result in results:
        lines.append(f"### {context}: {result.state}")
        lines.append(f"Description: {result.description}")
        tail = "\n".join(result.log.splitlines()[-LOG_TAIL_LINES:])
        lines.extend(["", "```text", tail, "```", ""])
    return "\n".join(lines)


def repo_state(state: dict[str, Any], owner: str, repo: str) -> dict[str, Any]:
    repos = state.setdefault("repos", {})
    return repos.setdefault(f"{owner}/{repo}", {"last_heads": [], "comments": {}})


def process_pr(config: dict[str, Any], repo_cfg: dict[str, Any], pr: dict[str, Any], state: dict[str, Any], runner=run_command) -> int:
    owner = repo_cfg.get("owner") or config["owner"]
    repo = repo_cfg["name"]
    sha = pr["headRefOid"]
    worktree_root = Path(config["worktree_root"]).expanduser()
    timeout = int(repo_cfg.get("job_timeout_seconds", config["job_timeout_seconds"]))
    repo_path = prepare_repo(owner, repo, resolve_repo_path(config, repo_cfg), runner)
    fetch_pr_head(repo_path, int(pr["number"]), runner)
    worktree = create_worktree(repo_path, sha, worktree_root, runner)
    results: list[tuple[str, JobResult]] = []
    try:
        for workflow, job_name, job in find_jobs(worktree):
            context = f"local-ci/{workflow}/{job_name}"
            post_status(owner, repo, sha, context, "pending", "local-ci running", runner)
            result = run_job(job, worktree, timeout, runner)
            target_url = None
            if os.environ.get("LOCAL_CI_GIST") == "1":
                target_url = create_log_gist(context, result.log, runner)
            post_status(owner, repo, sha, context, result.state, result.description, runner, target_url)
            results.append((context, result))
    finally:
        remove_worktree(worktree, runner)
    if results and os.environ.get("LOCAL_CI_GIST") != "1":
        post_comment(owner, repo, int(pr["number"]), build_comment(repo, sha, results), runner)
    repo_state(state, owner, repo)["last_heads"].append(sha)
    return 1 if any(result.state != "success" for _, result in results) else 0


def run_once(config: dict[str, Any], runner=run_command) -> int:
    state_dir = Path(config["state_dir"]).expanduser()
    state = load_state(state_dir)
    exit_code = 0
    for repo_cfg in config.get("repos") or []:
        owner = repo_cfg.get("owner") or config["owner"]
        repo = repo_cfg["name"]
        seen = set(repo_state(state, owner, repo).get("last_heads", []))
        for pr in gh_prs(owner, repo, runner):
            sha = pr.get("headRefOid")
            if not sha or sha in seen:
                continue
            exit_code = max(exit_code, process_pr(config, repo_cfg, pr, state, runner))
    save_state(state_dir, state)
    return exit_code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local pull_request CI for configured private repositories.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    try:
        return run_once(load_config(args.config))
    except Exception as exc:
        print(f"local-ci: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
