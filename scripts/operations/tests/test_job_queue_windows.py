import json
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "scripts" / "operations" / "job-queue-windows"


def run(cmd, cwd=None, env=None, check=True):
    merged = os.environ.copy()
    merged.update(env or {})
    merged["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=merged,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"{cmd} failed\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def git(cmd, cwd, check=True):
    return run(["git", *cmd], cwd=cwd, check=check)


def make_repo(tmp_path, job_id="done"):
    queue = tmp_path / "queue"
    clones = tmp_path / "clones"
    worktrees = tmp_path / "worktrees"
    remote = tmp_path / "remote.git"
    queue.mkdir()
    (queue / "jobs").mkdir()
    (queue / "logs").mkdir()
    (queue / "locks").mkdir()
    clones.mkdir()
    worktrees.mkdir()
    git(["init", "--bare", str(remote)], tmp_path)
    clone = clones / "example-repo"
    git(["clone", str(remote), str(clone)], tmp_path)
    git(["config", "user.email", "tester@example.invalid"], clone)
    git(["config", "user.name", "Tester"], clone)
    write_text(clone / "README.md", "base\n")
    git(["add", "README.md"], clone)
    git(["commit", "-m", "initial"], clone)
    git(["branch", "-M", "main"], clone)
    git(["push", "-u", "origin", "main"], clone)
    git(["worktree", "add", "-b", f"codex/cxl-{job_id}", str(worktrees / f"example-repo-cxl-{job_id}"), "origin/main"], clone)
    wt = worktrees / f"example-repo-cxl-{job_id}"
    git(["-C", str(wt), "push", "-u", "origin", f"codex/cxl-{job_id}"], tmp_path)
    write_text(queue / "jobs" / f"{job_id}.md", "REPO: example-repo\n")
    write_text(queue / "logs" / f"{job_id}.result", "OK abc pull\n")
    config = tmp_path / "job-queue.local.conf"
    write_text(
        config,
        "\n".join(
            [
                f"QUEUE_ROOT={queue.as_posix()}",
                f"CLONE_ROOT={clones.as_posix()}",
                f"WORKTREE_ROOT={worktrees.as_posix()}",
                "REPOSITORY_OWNER=example-owner",
                "DEFAULT_REPOSITORY=example-repo",
                "REPOSITORY_ALLOW_LIST=example-repo",
                "MIN_DISK_FREE_GB=50",
                "",
            ]
        ),
    )
    return queue, clones, worktrees, wt, config


def workspace_tmp():
    root = Path(os.environ.get("TMPDIR") or os.environ.get("TMP") or os.environ.get("TEMP") or ".")
    path = root / f"job-queue-test-{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    return path


def test_finished_pushed_clean_worktree_is_removed():
    tmp_path = workspace_tmp()
    _, _, _, wt, config = make_repo(tmp_path, "done")
    result = run(["bash", str(SCRIPT_DIR / "run-job.sh"), "cleanup", "done", "none", str(config)])
    assert result.returncode == 0
    assert not wt.exists()


def test_unpublished_dirty_untracked_and_referenced_worktrees_are_kept():
    tmp_path = workspace_tmp()
    queue, clones, worktrees, wt, config = make_repo(tmp_path, "kept")
    git(["checkout", "-b", "local-only"], wt)
    run(["bash", str(SCRIPT_DIR / "run-job.sh"), "cleanup", "kept", "none", str(config)])
    kept = (queue / "logs" / "kept-worktrees.tsv").read_text(encoding="utf-8")
    assert "head is not on its remote branch" in kept

    shutil.rmtree(tmp_path / "second", ignore_errors=True)
    queue, clones, worktrees, wt, config = make_repo(tmp_path / "second", "dirty")
    write_text(wt / "README.md", "changed\n")
    run(["bash", str(SCRIPT_DIR / "run-job.sh"), "cleanup", "dirty", "none", str(config)])
    kept = (queue / "logs" / "kept-worktrees.tsv").read_text(encoding="utf-8")
    assert "changed or untracked files" in kept

    queue, clones, worktrees, wt, config = make_repo(tmp_path / "third", "untracked")
    write_text(wt / "new.txt", "new\n")
    run(["bash", str(SCRIPT_DIR / "run-job.sh"), "cleanup", "untracked", "none", str(config)])
    kept = (queue / "logs" / "kept-worktrees.tsv").read_text(encoding="utf-8")
    assert "changed or untracked files" in kept

    queue, clones, worktrees, wt, config = make_repo(tmp_path / "fourth", "referenced")
    write_text(queue / "queue.txt", "later 1\n")
    write_text(queue / "jobs" / "later.md", "BASE_REF: codex/cxl-referenced\n")
    run(["bash", str(SCRIPT_DIR / "run-job.sh"), "cleanup", "referenced", "none", str(config)])
    kept = (queue / "logs" / "kept-worktrees.tsv").read_text(encoding="utf-8")
    assert "named by pending work" in kept


def test_pump_holds_when_either_disk_is_under_floor():
    tmp_path = workspace_tmp()
    queue, _, _, _, config = make_repo(tmp_path, "disk")
    write_text(queue / "queue.txt", "disk 1\n")
    launcher = tmp_path / "launcher.ps1"
    write_text(launcher, "throw 'launcher must not run'\n")
    env = {
        "JOB_QUEUE_TEST_FREE_GB_JSON": json.dumps({"clone": 49, "worktree": 100}),
        "JOB_QUEUE_TEST_LAUNCHER": str(launcher),
    }
    result = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT_DIR / "pump.ps1"), "-ConfigPath", str(config), "-Once"], env=env)
    assert result.returncode == 0
    log = (queue / "pump.log").read_text(encoding="ascii")
    assert "reason=clone-disk-under-50GB" in log

    (queue / "pump.log").unlink()
    env["JOB_QUEUE_TEST_FREE_GB_JSON"] = json.dumps({"clone": 100, "worktree": 49})
    result = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT_DIR / "pump.ps1"), "-ConfigPath", str(config), "-Once"], env=env)
    assert result.returncode == 0
    log = (queue / "pump.log").read_text(encoding="ascii")
    assert "reason=worktree-disk-under-50GB" in log


def test_path_limit_accepts_short_root_and_refuses_overlong_root():
    tmp_path = workspace_tmp()
    _, _, _, _, config = make_repo(tmp_path, "path")
    ok = run(["bash", str(SCRIPT_DIR / "run-job.sh"), "path-check", "path", "none", str(config), "a" * 120])
    assert ok.returncode == 0
    long_config = tmp_path / "long.conf"
    text = config.read_text(encoding="utf-8")
    long_root = (tmp_path / ("w" * 180)).as_posix()
    long_config.write_text(text.replace(f"WORKTREE_ROOT={(tmp_path / 'worktrees').as_posix()}", f"WORKTREE_ROOT={long_root}"), encoding="utf-8", newline="\n")
    bad = run(["bash", str(SCRIPT_DIR / "run-job.sh"), "path-check", "path", "none", str(long_config), "b" * 120], check=False)
    assert bad.returncode != 0
    assert "260 character limit" in bad.stdout


def test_public_scripts_are_neutralized_and_live_copy_lacks_new_behavior():
    files = [
        SCRIPT_DIR / "pump.ps1",
        SCRIPT_DIR / "run-job.sh",
        SCRIPT_DIR / "launch.ps1",
        SCRIPT_DIR / "launch.sh",
        SCRIPT_DIR / "limits.txt",
        SCRIPT_DIR / "job-queue.local.example.conf",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in files)
    assert not re.search(r"[A-Za-z]:[\\/]", text)
    assert "example-repo" in text
    assert "<queue-root>" in text
    assert "REPOSITORY_OWNER=<repository-owner>" in text
    assert "DEFAULT_REPOSITORY=example-repo" in text
    live = (Path(os.environ["PUMP2_SCRATCH"]) / "live-run-job.sh").read_text(encoding="utf-8")
    assert "cleanup_worktree" not in live
    assert "WORKTREE_ROOT" not in live
