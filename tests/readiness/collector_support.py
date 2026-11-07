"""Controlled collector subprocess environments; no installed SDK is imported."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROBE_LIB = REPO / "scripts/readiness/lib/probe-solvers.sh"
GIT_BINDINGS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE")


def bash_path(path: Path | str) -> str:
    """Convert native paths before embedding them in Bash text or PATH."""
    try:
        return subprocess.check_output(["cygpath", "-u", str(path)], text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return str(path)


def native_path(path: str) -> Path:
    """Construct a native Path from either native or MSYS spelling."""
    if os.name == "nt":
        path = subprocess.check_output(["cygpath", "-w", path], text=True).strip()
    return Path(path)


def collector_env(env: dict[str, str], *, stub_dirs: tuple[Path, ...] = ()) -> dict[str, str]:
    """Keep fixture files, SDK outcomes and child Git roots independent of the caller.

    BASH_ENV overrides the discovery primitives after sourcing the production library.
    The library's existing source guard retains these overrides in the collector.
    Only explicit stub directories may precede the SDK-blocking interpreter shims.
    """
    env = dict(env)
    for name in GIT_BINDINGS:
        env.pop(name, None)
    workspace = env.get("WORKSPACE_HUB")
    root = native_path(workspace).parent if workspace else native_path(env["TEST_ROOT"])
    scratch = root / "collector-runtime"
    scratch.mkdir(parents=True, exist_ok=True)
    home = scratch / "home"
    home.mkdir(exist_ok=True)
    temp = scratch / "tmp"
    temp.mkdir(exist_ok=True)
    installs = scratch / "installs"
    installs.mkdir(exist_ok=True)
    bindir = scratch / "bin"
    bindir.mkdir(exist_ok=True)
    stub = (
        '#!/usr/bin/env bash\n'
        'if [[ "${1:-}" == -c && "${2:-}" == "import OrcFxAPI" ]]; then exit 1; fi\n'
        f'exec {shlex.quote(bash_path(Path(sys.executable)))} "$@"\n'
    )
    for name in ("python", "python3"):
        path = bindir / name
        path.write_text(stub, encoding="utf-8", newline="\n")
        path.chmod(0o755)
    # Provenance tests use this helper directly, without the serialization suite's
    # autouse guard. Default to an empty synthetic schedule and unavailable tools;
    # explicit stub_dirs retain precedence for tests with controlled tool output.
    for name in ("crontab", "schtasks", "gh", "uv", "claude", "codex", "hermes", "gemini"):
        path = bindir / name
        body = "exit 0\n" if name in ("crontab", "schtasks") else "exit 1\n"
        path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8", newline="\n")
        path.chmod(0o755)  # POSIX executable permissions, as for the interpreter shims.
    startup = scratch / "startup.sh"
    startup.write_text(
        f'source {shlex.quote(bash_path(PROBE_LIB))}\n'
        '_ps_install_root() { printf "%s/%s" "$TEST_INSTALL_ROOT" "$1"; }\n',
        encoding="utf-8", newline="\n",
    )
    parts = [*(bash_path(path) for path in stub_dirs), bash_path(bindir),
             env.get("PATH", BASH_PATH)]
    env.update(PATH=":".join(parts), BASH_ENV=bash_path(startup),
               TEST_INSTALL_ROOT=bash_path(installs), TMPDIR=bash_path(temp),
               HOME=env.get("HOME", bash_path(home)), PYTHONDONTWRITEBYTECODE="1",
               GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    for name in ("WORKSPACE_HUB", "HOME", "ORCAWAVE_PATH"):
        if env.get(name):
            env[name] = bash_path(env[name])
    for name in ("SYSTEMROOT", "WINDIR", "COMSPEC"):
        if name in os.environ:
            env.setdefault(name, os.environ[name])
    return env


SCRIPT = REPO / "scripts" / "readiness" / "collect-equality.sh"
BASH_PATH = "/mingw64/bin:/usr/bin:/bin:/usr/local/bin"


def _fixture(tmp_path: Path) -> Path:
    """Minimal WORKSPACE_HUB tree the collector reads."""
    ws = tmp_path / "workspace-hub"
    (ws / ".claude" / "skills" / "cat" / "skillA").mkdir(parents=True)
    (ws / ".claude" / "skills" / "cat" / "skillA" / "SKILL.md").write_text("x")
    (ws / ".claude" / "dispatch").mkdir(parents=True)
    (ws / ".claude" / "dispatch" / "machine-a.yaml").write_text("x")
    (ws / ".claude" / "dispatch" / "multi.yaml").write_text("x")
    (ws / ".claude" / "memory").mkdir(parents=True)
    (ws / ".claude" / "memory" / "context.md").write_text("ctx")
    (ws / ".claude" / "state").mkdir(parents=True)
    (ws / ".claude" / "state" / "harness-readiness-machine-a.yaml").write_text(
        "overall: fail\npass_count: 17\n")
    # sibling tier-1 repo (not nested) — exercises bare-name + sibling mode
    (tmp_path / "digitalmodel" / ".git").mkdir(parents=True)
    return ws


