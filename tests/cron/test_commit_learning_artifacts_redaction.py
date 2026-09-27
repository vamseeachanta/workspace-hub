"""C20: commit-learning-artifacts.sh redacts host state before it enters the
public tree, and stops when the redactor cannot load.

The script used to ``cp`` the raw codex ``history.jsonl`` (and other host agent
state) into this PUBLIC repository. Each host copy now goes through
``scripts/legal/public_redaction.py copy``; a memory file whose name carries an
identifier is not copied at all; and the script refuses to snapshot anything
when the redactor cannot load. The run happens in a disposable repository with
a disposable HOME, and inherited Git bindings are cleared. Names are synthetic.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "cron" / "commit-learning-artifacts.sh"
SYNTH = "zorblaxcorp"

NEEDED = [
    "scripts/cron/commit-learning-artifacts.sh",
    "scripts/cron/lib/pii-safe-memory-snapshot.sh",
    "scripts/legal/public_redaction.py",
    "scripts/legal/check_identifiers.py",
    ".legal-identifier-gate.yaml",
]


def _bash() -> str | None:
    b = shutil.which("bash")
    if not b:
        return None
    if os.name == "nt" and "system32" in b.lower():
        return None  # the WSL launcher, not a POSIX bash for this tree
    return b


def test_no_raw_copy_of_host_state_into_the_public_tree():
    text = SCRIPT.read_text(encoding="utf-8")
    for host_file in ("history.jsonl", "session_index.jsonl", "state.json", "projects.json",
                      "MEMORY.md", "USER.md", "default.rules"):
        for line in text.splitlines():
            if host_file in line and line.strip().startswith("cp "):
                pytest.fail(f"raw cp of host file remains: {line.strip()}")
    assert "public_redaction.py" in text
    assert "self-check" in text


def _setup(tmp_path: Path, deny: Path | None):
    repo = tmp_path / "repo"
    for rel in NEEDED:
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dest)
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    (home / ".codex" / "history.jsonl").write_text(
        '{"session_id":"s1","text":"work on the %s riser"}\n{"session_id":"s2","text":"clean"}\n' % SYNTH,
        encoding="utf-8",
    )
    mem = home / ".claude" / "projects" / "-mnt-local-analysis-workspace-hub" / "memory"
    mem.mkdir(parents=True)
    (mem / "feedback_a.md").write_text(f"lesson about {SYNTH}\n", encoding="utf-8")
    (mem / f"crossprovider_{SYNTH}_lifecycle_ab12.md").write_text("clean body\n", encoding="utf-8")
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                        "PII_CODENAME_MAP", "LEGAL_CLIENT_MAP", "WORKSPACE_HUB_DENY_LIST")}
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["WORKSPACE_HUB_PYTHON"] = sys.executable
    env["PII_CODENAME_MAP"] = str(tmp_path / "no-map.yaml")
    if deny is not None:
        env["WORKSPACE_HUB_DENY_LIST"] = str(deny)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, env=env)
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "add", "-A"],
                   cwd=repo, check=True, env=env)
    subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "seed"],
                   cwd=repo, check=True, env=env)
    return repo, env


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_run_redacts_host_copies_and_skips_name_bearing_files(tmp_path):
    deny = tmp_path / "deny.txt"
    deny.write_text(f"{SYNTH}\n", encoding="utf-8")
    repo, env = _setup(tmp_path, deny)
    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh", "--dry-run"],
                       cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    hist = repo / "config/agents/codex/state-snapshots/history.jsonl"
    assert hist.exists()
    assert SYNTH not in hist.read_text(encoding="utf-8").lower()
    assert '"clean"' in hist.read_text(encoding="utf-8")
    snaps = repo / "config/agents/claude/memory-snapshots"
    names = [p.name for p in snaps.iterdir()] if snaps.exists() else []
    assert not any(SYNTH in n.lower() for n in names)
    for p in snaps.glob("*.md") if snaps.exists() else []:
        assert SYNTH not in p.read_text(encoding="utf-8").lower()
    assert SYNTH not in (r.stdout + r.stderr).lower()


@pytest.mark.skipif(_bash() is None, reason="no POSIX bash")
def test_run_fails_closed_without_the_redactor(tmp_path):
    repo, env = _setup(tmp_path, tmp_path / "missing-deny.txt")
    r = subprocess.run([_bash(), "scripts/cron/commit-learning-artifacts.sh", "--dry-run"],
                       cwd=repo, env=env, capture_output=True, text=True)
    assert r.returncode != 0
    assert not (repo / "config/agents/codex/state-snapshots/history.jsonl").exists()
    assert not (repo / "config/agents/claude/memory-snapshots").exists()
