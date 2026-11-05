"""Exercise a real fast-forward collision without touching any shared checkout."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_untracked_collision_stops_and_preserves_file(tmp_path):
    env = {k: v for k, v in os.environ.items()
           if k not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"}}
    for key in tuple(env):
        if key.startswith(("GIT_CONFIG_", "GIT_AUTHOR_", "GIT_COMMITTER_")):
            env.pop(key)
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["LC_ALL"] = "C"
    def git(cwd, *args):
        return subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture", *args], cwd=cwd, env=env, check=True,
                              capture_output=True, text=True).stdout.strip()
    source, local = tmp_path / "source", tmp_path / "local"
    source.mkdir()
    git(source, "init", "-b", "main")
    git(source, "commit", "--allow-empty", "-m", "test: initial fixture")
    git(tmp_path, "clone", str(source), str(local))
    path = "docs/reports/collision matrix.html"
    incoming = source / path
    incoming.parent.mkdir(parents=True)
    incoming.write_text("incoming\n", encoding="utf-8", newline="\n")
    git(source, "add", "--", path)
    git(source, "commit", "-m", "test: incoming fixture", "--", path)
    user_file = local / path
    user_file.parent.mkdir(parents=True)
    user_file.write_text("local evidence\n", encoding="utf-8", newline="\n")
    before = git(local, "rev-parse", "HEAD")
    proc = subprocess.run(["bash", str(ROOT / "scripts/solver/watch-results.sh"), "--once"],
                          cwd=local, env=env, text=True, capture_output=True, timeout=30)
    assert proc.returncode != 0
    assert "untracked file collision" in proc.stdout + proc.stderr
    assert path in proc.stdout + proc.stderr
    assert "(1/3)" not in proc.stdout + proc.stderr
    assert user_file.read_text(encoding="utf-8") == "local evidence\n"
    assert git(local, "rev-parse", "HEAD") == before
    assert "untracked file collision" in (local / "queue/.watcher-state/git-pull-failures.log").read_text(encoding="utf-8")
