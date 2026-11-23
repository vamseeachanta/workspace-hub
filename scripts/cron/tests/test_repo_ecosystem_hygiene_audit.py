"""Tests for the read-only repo ecosystem hygiene audit."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "repo-ecosystem-hygiene-audit.sh"
REGISTRY = REPO_ROOT / "config" / "workstations" / "registry.yaml"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"


def run(cmd: list[str], cwd: Path, **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, **kwargs)


def make_git_repo(path: Path, *, untracked: bool = False) -> None:
    path.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-b", "main"], path, check=True)
    (path / "README.md").write_text(f"# {path.name}\n")
    run(["git", "add", "README.md"], path, check=True)
    run(
        [
            "git",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "user.name=Test User",
            "commit",
            "-m",
            "initial",
        ],
        path,
        check=True,
    )
    remote_root = path.parent.parent / "remotes"
    remote_root.mkdir(exist_ok=True)
    remote = remote_root / f"{path.name}.git"
    run(["git", "init", "--bare", str(remote)], path, check=True)
    run(["git", "remote", "add", "origin", str(remote)], path, check=True)
    run(["git", "push", "-u", "origin", "main"], path, check=True)
    if untracked:
        (path / "untracked.txt").write_text("local residue\n")


def git(cmd: list[str], repo: Path, **kwargs) -> subprocess.CompletedProcess[str]:
    return run(["git", *cmd], repo, check=True, **kwargs)


def old_git_env() -> dict[str, str]:
    env = os.environ.copy()
    old = (datetime.now(timezone.utc) - timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%S+0000")
    env["GIT_AUTHOR_DATE"] = old
    env["GIT_COMMITTER_DATE"] = old
    return env


def tier1_baseline() -> dict:
    data = yaml.safe_load(REGISTRY.read_text())
    return data["machines"]["dev-primary"]["tier1_baseline"]


def required_repos() -> list[str]:
    return tier1_baseline()["required"]


def governed_repos_from_registry() -> tuple[list[str], dict[str, str]]:
    baseline = tier1_baseline()
    classes: dict[str, str] = {}
    ordered: list[str] = []
    for cls in ("required", "optional", "non_tier1_machine_access_current"):
        for name in baseline.get(cls, []) or []:
            if name not in classes:
                classes[name] = cls
                ordered.append(name)
    return ordered, classes


def schedule_by_id(task_id: str) -> str:
    data = yaml.safe_load(SCHEDULE.read_text())
    for task in data["tasks"]:
        if task.get("id") == task_id:
            return task["schedule"]
    raise AssertionError(f"missing scheduled task: {task_id}")


def daily_cron_second(schedule: str) -> int:
    minute, hour, dom, month, dow = schedule.split()
    assert dom == month == dow == "*"
    return int(hour) * 3600 + int(minute) * 60


def audit_env(tmp_path: Path) -> tuple[dict[str, str], Path, Path]:
    ecosystem = tmp_path / "ecosystem"
    workspace = ecosystem / "workspace-hub"
    output = tmp_path / "out"
    ecosystem.mkdir()
    make_git_repo(workspace)
    env = os.environ.copy()
    env.update(
        {
            "WORKSPACE_HUB": str(workspace),
            "REPO_ECOSYSTEM_ROOT": str(ecosystem),
            "REPO_ECOSYSTEM_HYGIENE_OUTPUT_DIR": str(output),
            "REPO_ECOSYSTEM_HYGIENE_HOSTNAME": "ace-linux-1",
            "REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC": "2",
            "REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC": "5",
            "REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC": "30",
            "REPO_ECOSYSTEM_HYGIENE_SKIP_GH": "1",
            "UV_CACHE_DIR": str(REPO_ROOT / ".claude" / "state" / "uv-cache"),
        }
    )
    return env, ecosystem, output


def load_latest_state(output: Path) -> dict:
    latest = output / "latest.json"
    assert latest.exists(), f"missing JSON state: {latest}"
    return json.loads(latest.read_text())


def test_script_syntax_ok() -> None:
    result = run(["bash", "-n", str(SCRIPT)], REPO_ROOT)
    assert result.returncode == 0, result.stderr


def test_static_readonly_contract() -> None:
    text = SCRIPT.read_text()
    assert "def git_readonly(" in text
    assert "def gh_readonly(" in text
    assert "def fs_write(" in text
    assert "GIT_OPTIONAL_LOCKS" in text
    assert "git stash list --date=iso-strict --format=%gd%x1f%ci%x1f%s" in text
    assert "--paginate" not in text
    assert text.count("subprocess.run(") == 1
    assert '["timeout", str(allowed_timeout), *command]' in text
    assert "def fallback_default_branch(repo: Path, timeout_sec: float | None = None)" in text
    assert "return fallback_default_branch(repo, timeout_sec=timeout_sec)" in text

    forbidden = [
        r"\bgit\s+add\b",
        r"\bgit\s+commit\b",
        r"\bgit\s+push\b",
        r"\bgit\s+pull\b",
        r"\bgit\s+merge\b",
        r"\bgit\s+rebase\b",
        r"\bgit\s+reset\b",
        r"\bgit\s+checkout\b",
        r"\bgit\s+switch\b",
        r"\bgit\s+clean\b",
        r"\bgit\s+worktree\s+prune\b",
        r"\bgh\s+issue\s+(comment|edit|close)\b",
        r"\bgh\s+pr\s+merge\b",
        r"\brm\s+-(f|r|rf|fr)\b",
        r"\brmdir\b",
        r"\bunlink\b",
        r"\bfind\b.*\s-delete\b",
        r"\bfind\b.*\s-exec\s+rm\b",
        r"\bxargs\s+rm\b",
        r"\beval\b",
        r"bash\s+-c.*git",
        r'\["git",\s*"add"\]',
        r'\["git",\s*"commit"\]',
        r'\["git",\s*"push"\]',
        r'\["git",\s*"pull"\]',
        r'\["git",\s*"merge"\]',
        r'\["git",\s*"rebase"\]',
        r'\["git",\s*"reset"\]',
        r'\["git",\s*"checkout"\]',
        r'\["git",\s*"switch"\]',
        r'\["git",\s*"worktree",\s*"remove"(?:\s*,|\])',
        r'\["git",\s*"worktree",\s*"prune"(?:\s*,|\])',
        r'\["git",\s*"stash",\s*"drop"(?:\s*,|\])',
        r'\["git",\s*"stash",\s*"pop"(?:\s*,|\])',
        r'\["git",\s*"stash",\s*"push"(?:\s*,|\])',
        r'\["git",\s*"branch",\s*"-[dD]"(?:\s*,|\])',
        r'\["git",\s*"update-ref"(?:\s*,|\])',
        r'\["gh",\s*"issue",\s*"(comment|edit|close)"\]',
        r'\["gh",\s*"pr",\s*"merge"\]',
        r'\["gh",\s*"api"(?:[^\]]*,){0,5}\s*"-X"\s*,\s*"(POST|PATCH|PUT|DELETE)"',
        r'\["rm"',
        r'\["rmdir"',
        r'\["unlink"',
    ]
    for pattern in forbidden:
        assert not re.search(pattern, text), f"forbidden token matched: {pattern}"


def test_repo_hygiene_timeout_defaults_are_production_safe() -> None:
    text = SCRIPT.read_text()
    probe = re.search(r'PROBE_TIMEOUT_SEC = int\(os\.environ\.get\("REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC", "(\d+)"\)\)', text)
    repo = re.search(r'REPO_TIMEOUT_SEC = int\(os\.environ\.get\("REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC", "(\d+)"\)\)', text)
    total_shell = re.search(r'TOTAL_TIMEOUT="\$\{REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC:-(\d+)\}"', text)
    total_python = re.search(r'TOTAL_TIMEOUT_SEC = int\(os\.environ\.get\("REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC", "(\d+)"\)\)', text)
    assert probe and int(probe.group(1)) == 30
    assert repo and int(repo.group(1)) == 120
    assert total_shell and int(total_shell.group(1)) == 480
    assert total_python and int(total_python.group(1)) == 480

    hygiene_time = daily_cron_second(schedule_by_id("repo-ecosystem-hygiene"))
    health_time = daily_cron_second(schedule_by_id("cron-health"))
    schedule_gap = (health_time - hygiene_time) % (24 * 3600)
    assert schedule_gap > 0
    assert int(total_shell.group(1)) < schedule_gap


def test_governed_repo_names_includes_required_optional_and_non_tier1(tmp_path: Path) -> None:
    env, ecosystem, output = audit_env(tmp_path)
    names, classes = governed_repos_from_registry()
    for repo in names:
        if repo != "workspace-hub":
            make_git_repo(ecosystem / repo)

    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env)
    assert result.returncode == 0, result.stderr + result.stdout
    state = load_latest_state(output)
    actual_classes = {repo["name"]: repo["class"] for repo in state["repos"]}
    assert set(tier1_baseline()["required"]).issubset(actual_classes)
    assert set(tier1_baseline()["optional"]).issubset(actual_classes)
    assert set(tier1_baseline()["non_tier1_machine_access_current"]).issubset(actual_classes)
    for repo, cls in classes.items():
        assert actual_classes[repo] == cls


def test_top_level_timeout_emits_execution_failure_marker(tmp_path: Path) -> None:
    uv_shim = tmp_path / "uv"
    uv_shim.write_text("#!/usr/bin/env bash\nsleep 3\n")
    uv_shim.chmod(0o755)
    env = os.environ.copy()
    env.update(
        {
            "UV_BIN": str(uv_shim),
            "REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC": "1",
        }
    )
    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env)
    assert result.returncode != 0
    assert "ERROR: repo-ecosystem-hygiene execution_failed" in result.stdout


def test_probe_timeout_is_bounded_and_reported(tmp_path: Path) -> None:
    env, ecosystem, output = audit_env(tmp_path)
    for repo in required_repos():
        if repo != "workspace-hub":
            make_git_repo(ecosystem / repo)

    real_git = shutil.which("git")
    assert real_git
    git_shim = tmp_path / "git"
    git_shim.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == \"status\" ]]; then sleep 3; exit 0; fi\n"
        f"exec {real_git} \"$@\"\n"
    )
    git_shim.chmod(0o755)
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    env["REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC"] = "1"
    env["REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC"] = "20"

    start = time.monotonic()
    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env)
    elapsed = time.monotonic() - start
    assert result.returncode == 0, result.stderr + result.stdout
    assert elapsed < 20
    state = load_latest_state(output)
    assert state["status"] == "ERROR"
    assert any(
        finding["code"] == "git_probe_timeout"
        for repo in state["repos"]
        for finding in repo.get("findings", [])
    )


def test_status_short_probe_uses_default_timeout_budget(tmp_path: Path) -> None:
    env, _ecosystem, output = audit_env(tmp_path)
    env.pop("REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC")
    env.pop("REPO_ECOSYSTEM_HYGIENE_REPO_TIMEOUT_SEC")
    env["REPO_ECOSYSTEM_HYGIENE_TOTAL_TIMEOUT_SEC"] = "70"

    real_git = shutil.which("git")
    assert real_git
    git_shim = tmp_path / "git"
    git_shim.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == \"status\" ]]; then sleep 12; exit 0; fi\n"
        f"exec {real_git} \"$@\"\n"
    )
    git_shim.chmod(0o755)
    env["PATH"] = f"{tmp_path}:{env['PATH']}"

    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env, timeout=80)
    assert result.returncode == 0, result.stderr + result.stdout
    state = load_latest_state(output)
    assert not any(
        finding["code"] == "git_probe_timeout"
        for repo in state["repos"]
        for finding in repo.get("findings", [])
    )

    env["REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC"] = "1"
    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env, timeout=30)
    assert result.returncode == 0, result.stderr + result.stdout
    state = load_latest_state(output)
    assert any(
        finding["code"] == "git_probe_timeout"
        for repo in state["repos"]
        for finding in repo.get("findings", [])
    )


def test_audit_writes_local_reports_and_missing_required_is_error(tmp_path: Path) -> None:
    env, ecosystem, output = audit_env(tmp_path)
    for repo in required_repos():
        if repo in {"workspace-hub", "llm-wiki"}:
            continue
        make_git_repo(ecosystem / repo)

    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "task=repo-ecosystem-hygiene status=ERROR" in result.stdout
    assert "ERROR:" not in result.stdout
    assert "fatal:" not in result.stdout

    state = load_latest_state(output)
    assert state["status"] == "ERROR"
    llm_wiki = next(repo for repo in state["repos"] if repo["name"] == "llm-wiki")
    assert llm_wiki["status"] == "ERROR"
    assert llm_wiki["findings"][0]["code"] == "missing_required_checkout"
    assert (output / "latest.md").exists()
    assert not list((REPO_ROOT / "docs" / "reports").glob("repo-ecosystem-hygiene*.md"))


def test_unknown_git_and_non_git_sibling_residue_are_warn(tmp_path: Path) -> None:
    env, ecosystem, output = audit_env(tmp_path)
    for repo in required_repos():
        if repo != "workspace-hub":
            make_git_repo(ecosystem / repo)
    make_git_repo(ecosystem / "deckhand")
    (ecosystem / "scratch-residue").mkdir()

    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env)
    assert result.returncode == 0, result.stderr + result.stdout
    state = load_latest_state(output)

    residue = {item["name"]: item for item in state["residue"]}
    assert residue["deckhand"]["status"] == "WARN"
    assert residue["deckhand"]["finding"] == "registry_disposition_required"
    assert residue["scratch-residue"]["status"] == "WARN"
    assert residue["scratch-residue"]["finding"] == "unknown_sibling_residue"


def test_dirty_status_includes_untracked_repo_files(tmp_path: Path) -> None:
    env, ecosystem, output = audit_env(tmp_path)
    for repo in required_repos():
        if repo == "workspace-hub":
            continue
        make_git_repo(ecosystem / repo, untracked=(repo == "digitalmodel"))

    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env)
    assert result.returncode == 0, result.stderr + result.stdout
    state = load_latest_state(output)
    digitalmodel = next(repo for repo in state["repos"] if repo["name"] == "digitalmodel")
    assert digitalmodel["status"] == "WARN"
    assert any(finding["code"] == "dirty_worktree" for finding in digitalmodel["findings"])
    assert digitalmodel["dirty_count"] == 1


def test_historical_entry_precedence_over_unknown_residue(tmp_path: Path) -> None:
    env, ecosystem, output = audit_env(tmp_path)
    for repo in required_repos():
        if repo != "workspace-hub":
            make_git_repo(ecosystem / repo)
    make_git_repo(ecosystem / "mkt-a")

    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env)
    assert result.returncode == 0, result.stderr + result.stdout
    state = load_latest_state(output)

    historical = {item["name"]: item for item in state["historical"]}
    assert historical["mkt-a"]["status"] == "WARN"
    assert historical["mkt-a"]["finding"] == "historical_state_changed_since_prior_comment"
    assert historical["mkt-a"]["latest_probe_mismatch"] is True
    assert "mkt-a" not in {item["name"] for item in state["residue"]}


def test_reports_stale_branch_worktree_and_stash(tmp_path: Path) -> None:
    env, ecosystem, output = audit_env(tmp_path)
    for repo in required_repos():
        if repo == "workspace-hub":
            continue
        make_git_repo(ecosystem / repo)

    repo = ecosystem / "digitalmodel"
    git(["switch", "-c", "stale-topic"], repo)
    (repo / "old.txt").write_text("old branch\n")
    git(["add", "old.txt"], repo)
    git(["-c", "user.email=test@example.invalid", "-c", "user.name=Test User", "commit", "-m", "old branch"], repo, env=old_git_env())
    git(["switch", "main"], repo)
    git(["worktree", "add", str(ecosystem / "digitalmodel-stale-worktree"), "stale-topic"], repo)

    stash_repo = ecosystem / "worldenergydata"
    (stash_repo / "README.md").write_text("# changed for stash\n")
    git(["stash", "push", "-m", "old-stash"], stash_repo, env=old_git_env())

    result = run(["bash", str(SCRIPT)], REPO_ROOT, env=env)
    assert result.returncode == 0, result.stderr + result.stdout
    state = load_latest_state(output)

    digitalmodel = next(repo for repo in state["repos"] if repo["name"] == "digitalmodel")
    assert digitalmodel["worktrees"]["stale_count"] >= 1
    assert digitalmodel["stale_branch_count"] >= 1
    assert any(finding["code"] == "stale_worktree" for finding in digitalmodel["findings"])
    assert any(finding["code"] == "stale_branch" for finding in digitalmodel["findings"])

    worldenergydata = next(repo for repo in state["repos"] if repo["name"] == "worldenergydata")
    assert worldenergydata["stash_count"] >= 1
    assert worldenergydata["stale_stash_count"] >= 1
    assert any(finding["code"] == "stale_stash" for finding in worldenergydata["findings"])
