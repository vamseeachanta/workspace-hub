"""Tests for config/tmux/tmux.conf and config/tmux/start-session.sh (#3784).

Two defects, both measured on the live fleet 2026-08-02.

**Silent plugin skip.** tmux.conf loads resurrect/continuum behind
`if-shell "[ -r ... ]"`, whose own comment reads "Machines without the plugins
skip this block silently." ace-linux-2 and gpu-claw hit exactly that: the
config sources cleanly, nothing is reported, and neither box has reboot
survival. Absence of signal read as success.

**Three competing session names.** The live sessions are `overnight`, the
deployed alias is `tmux new -A -s main`, and start-session.sh defaults to
`work`. So the committed launcher, the committed alias, and the actually
running sessions all disagree, and `-A` idempotency is defeated by the
mismatch.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TMUX_CONF = REPO_ROOT / "config" / "tmux" / "tmux.conf"
LAUNCHER = REPO_ROOT / "config" / "tmux" / "start-session.sh"

CANONICAL_SESSION = "main"


def directives(path: Path) -> str:
    """File contents with `#` comments stripped.

    Mandatory for every structural assertion here: a comment explaining why a
    setting is avoided necessarily contains that setting's name, so a
    whole-file grep tests the prose rather than the behaviour.
    """
    return "\n".join(
        line for line in path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )


# ── tmux.conf: the silent skip must become audible ────────────────────────


def test_conf_warns_when_plugins_are_absent() -> None:
    text = directives(TMUX_CONF)
    assert "display-message" in text, (
        "plugin absence must be reported, not inferred from missing behaviour"
    )


def test_conf_warning_fires_on_attach_not_at_load() -> None:
    """A config-load `display-message` has no client to display to.

    tmux sources its config when the SERVER starts, which is before any client
    exists, so a bare display-message in the else-branch is written to nobody.
    The warning has to be attached to the client-attached hook to be seen.
    """
    text = directives(TMUX_CONF)
    assert re.search(r"set-hook\s+-g\s+client-attached", text), (
        "warning must be bound to client-attached, or no operator ever sees it"
    )


def test_conf_still_loads_plugins_when_present() -> None:
    text = directives(TMUX_CONF)
    assert "resurrect.tmux" in text and "continuum.tmux" in text


def test_conf_keeps_generous_history() -> None:
    assert re.search(r"history-limit\s+50000", directives(TMUX_CONF))


# ── start-session.sh: one canonical session name ──────────────────────────


def run_launcher(hostname: str, tmp_path: Path) -> subprocess.CompletedProcess:
    """Run the launcher with a stub tmux, capturing the session name it uses."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    stub = bin_dir / "tmux"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$(dirname "$0")/tmux_calls"\n'
        '[[ "$1" == "has-session" ]] && exit 1\n'
        "exit 0\n"
    )
    stub.chmod(0o755)
    # `hostname` is stubbed rather than passed in an env var: the launcher
    # assigns HOST="$(hostname)", which OVERWRITES any inherited HOST, so an
    # env-var-only test would silently exercise the current machine's branch.
    hn = bin_dir / "hostname"
    hn.write_text(f"#!/usr/bin/env bash\necho {hostname}\n")
    hn.chmod(0o755)

    bash = shutil.which("bash") or "/bin/bash"
    subprocess.run(
        [bash, str(LAUNCHER)],
        env={"PATH": f"{bin_dir}:/usr/bin:/bin", "HOME": str(tmp_path)},
        capture_output=True, text=True, timeout=60,
    )
    calls = bin_dir / "tmux_calls"
    return calls.read_text() if calls.exists() else ""


def test_launcher_defaults_to_the_canonical_session(tmp_path: Path) -> None:
    calls = run_launcher("ace-linux-1", tmp_path)
    assert f"-s {CANONICAL_SESSION}" in calls, (
        f"launcher must default to '{CANONICAL_SESSION}', got:\n{calls}"
    )


def test_launcher_does_not_default_to_work(tmp_path: Path) -> None:
    """`work` was the third competing name; it must be gone."""
    assert not re.search(r'SESSION="\$\{1:-work\}"', LAUNCHER.read_text())


def test_launcher_resolves_gpu_claw(tmp_path: Path) -> None:
    """gpu-claw had no case at all and fell through to the default branch."""
    text = directives(LAUNCHER)
    assert "gpu-claw" in text
    assert "ws/workspace-hub" in text, "gpu-claw's root is ~/ws/workspace-hub (#3507)"


def test_launcher_drops_the_retired_node(tmp_path: Path) -> None:
    """vamsee-linux1 was removed from the tailnet; a stale case invites drift."""
    assert "vamsee-linux1" not in directives(LAUNCHER)


def test_launcher_hostname_is_injectable(tmp_path: Path) -> None:
    """Needed so the per-host branches are testable at all."""
    calls = run_launcher("gpu-claw", tmp_path)
    assert calls, "launcher produced no tmux calls under a stubbed hostname"
