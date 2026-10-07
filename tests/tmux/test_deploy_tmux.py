"""Tests for scripts/setup/deploy-tmux.sh (workspace-hub#3784).

This is the script that makes every other slice actually reach a machine. It
runs from scripts/setup/new-machine-setup.sh Step 8b, so it is also the first
thing a new box executes — which is why almost everything here degrades with a
message rather than failing.

The defects it must fix, each measured on the live fleet 2026-08-02:

* It only ever symlinked the config, never installed the resurrect/continuum
  plugins. That is the root cause of the per-machine drift: ace-linux-2 and
  gpu-claw have no plugins, and the shared config's `if-shell` guard skips the
  plugin block SILENTLY, so the boxes look configured and have no reboot
  survival.
* `ln -sf` overwrites a regular `~/.tmux.conf` with no backup. gpu-claw has a
  26-line hand-rolled file that would be destroyed without trace.
* Nothing installed the auto-attach block, so nothing put an SSH login into
  the persistent session.

TDD: written before the changes; expected to FAIL first.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DEPLOY = REPO_ROOT / "scripts" / "setup" / "deploy-tmux.sh"

SENTINEL_OPEN = ">>> workspace-hub tmux auto-attach >>>"
SENTINEL_CLOSE = "<<< workspace-hub tmux auto-attach <<<"


# ── Harness ───────────────────────────────────────────────────────────────


@pytest.fixture
def fake_home(tmp_path: Path) -> Path:
    home = tmp_path / "home"
    home.mkdir()
    (tmp_path / "bin").mkdir()
    # Stock Ubuntu shape: no ~/.bash_profile, ~/.profile sources ~/.bashrc.
    (home / ".profile").write_text(
        'if [ -n "$BASH_VERSION" ]; then\n'
        '    if [ -f "$HOME/.bashrc" ]; then\n'
        '        . "$HOME/.bashrc"\n'
        "    fi\n"
        "fi\n"
    )
    (home / ".bashrc").write_text("# existing user content\nalias ll='ls -l'\n")
    return home


def stub_bin(home: Path) -> Path:
    return home.parent / "bin"


def install_stubs(home: Path, *, git_fails: bool = False) -> None:
    """Stub tmux, git and systemctl so nothing touches the real machine."""
    b = stub_bin(home)

    (b / "tmux").write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$(dirname "$0")/tmux_calls"\n'
        '[[ "$1" == "list-sessions" ]] && exit 1\n'
        '[[ "$1" == "-V" ]] && { echo "tmux 3.4"; exit 0; }\n'
        "exit 0\n"
    )

    git_body = (
        'echo "stub: clone refused" >&2\nexit 1\n' if git_fails
        else
        # Emulate a real clone: materialise the file the guard checks for.
        'if [[ "$1" == "clone" ]]; then\n'
        '  dest="${@: -1}"\n'
        '  mkdir -p "$dest/scripts"\n'
        '  base="$(basename "$dest")"\n'
        '  printf "# stub plugin\\n" > "$dest/${base#tmux-}.tmux"\n'
        '  printf "#!/usr/bin/env bash\\n" > "$dest/scripts/save.sh"\n'
        '  chmod +x "$dest/scripts/save.sh"\n'
        "fi\n"
        "exit 0\n"
    )
    (b / "git").write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$(dirname "$0")/git_calls"\n' + git_body
    )

    (b / "systemctl").write_text("#!/usr/bin/env bash\nexit 1\n")

    for name in ("tmux", "git", "systemctl"):
        (b / name).chmod(0o755)


def run_deploy(home: Path) -> subprocess.CompletedProcess:
    bash = shutil.which("bash") or "/bin/bash"
    return subprocess.run(
        [bash, str(DEPLOY)],
        env={
            "PATH": f"{stub_bin(home)}:/usr/bin:/bin",
            "HOME": str(home),
        },
        capture_output=True,
        text=True,
        timeout=90,
    )


def calls(home: Path, name: str) -> list:
    f = stub_bin(home) / f"{name}_calls"
    return f.read_text().splitlines() if f.exists() else []


# ── Existing behaviour must survive ───────────────────────────────────────


def test_deploy_symlinks_the_shared_config(fake_home: Path) -> None:
    install_stubs(fake_home)
    result = run_deploy(fake_home)
    assert result.returncode == 0, result.stderr
    dest = fake_home / ".tmux.conf"
    assert dest.is_symlink()
    assert dest.resolve() == (REPO_ROOT / "config" / "tmux" / "tmux.conf").resolve()


# ── Never clobber without a backup ────────────────────────────────────────


def test_deploy_backs_up_a_regular_tmux_conf(fake_home: Path) -> None:
    """gpu-claw's live case: a hand-rolled regular file, not a symlink."""
    install_stubs(fake_home)
    original = "# hand-rolled config\nset -g prefix C-a\n"
    (fake_home / ".tmux.conf").write_text(original)

    run_deploy(fake_home)

    backups = list(fake_home.glob(".tmux.conf.bak-*"))
    assert backups, "a regular ~/.tmux.conf must be backed up before replacement"
    assert backups[0].read_text() == original
    assert (fake_home / ".tmux.conf").is_symlink()


def test_deploy_does_not_backup_an_already_correct_symlink(fake_home: Path) -> None:
    """Re-running onboarding must not litter the home directory."""
    install_stubs(fake_home)
    run_deploy(fake_home)
    run_deploy(fake_home)
    assert list(fake_home.glob(".tmux.conf.bak-*")) == []


# ── Plugin installation — the drift root cause ────────────────────────────


def test_deploy_installs_missing_plugins(fake_home: Path) -> None:
    install_stubs(fake_home)
    run_deploy(fake_home)
    plugins = fake_home / ".tmux" / "plugins"
    assert (plugins / "tmux-resurrect").is_dir()
    assert (plugins / "tmux-continuum").is_dir()


def test_deploy_pins_the_plugin_clone(fake_home: Path) -> None:
    """Unpinned clones let three machines get three different plugin versions,
    which contradicts the convergence this change exists to deliver."""
    install_stubs(fake_home)
    run_deploy(fake_home)
    clones = [c for c in calls(fake_home, "git") if c.startswith("clone")]
    assert clones, "expected git clone invocations"
    for c in clones:
        assert re.search(r"--branch|--depth|checkout|[0-9a-f]{7,40}", c), (
            f"clone is not pinned to a ref: {c}"
        )


def test_deploy_warns_but_succeeds_when_clone_fails(fake_home: Path) -> None:
    """No network on a fresh box must not fail onboarding — but must be loud."""
    install_stubs(fake_home, git_fails=True)
    result = run_deploy(fake_home)
    assert result.returncode == 0
    assert "warn" in (result.stdout + result.stderr).lower()


def test_deploy_revalidates_a_partial_plugin_dir(fake_home: Path) -> None:
    """A directory is not a plugin. A failed clone can leave an empty one."""
    install_stubs(fake_home)
    broken = fake_home / ".tmux" / "plugins" / "tmux-resurrect"
    broken.mkdir(parents=True)
    result = run_deploy(fake_home)
    combined = (result.stdout + result.stderr).lower()
    assert (broken / "resurrect.tmux").exists() or "warn" in combined, (
        "an incomplete plugin dir must be repaired or reported, not accepted"
    )


# ── The auto-attach block ─────────────────────────────────────────────────


def test_deploy_installs_the_autoattach_block(fake_home: Path) -> None:
    install_stubs(fake_home)
    run_deploy(fake_home)
    bashrc = (fake_home / ".bashrc").read_text()
    assert SENTINEL_OPEN in bashrc and SENTINEL_CLOSE in bashrc
    assert "autoattach.sh" in bashrc


def test_deploy_preserves_existing_bashrc(fake_home: Path) -> None:
    install_stubs(fake_home)
    run_deploy(fake_home)
    bashrc = (fake_home / ".bashrc").read_text()
    assert "# existing user content" in bashrc
    assert "alias ll='ls -l'" in bashrc


def test_deploy_block_install_is_idempotent(fake_home: Path) -> None:
    install_stubs(fake_home)
    run_deploy(fake_home)
    run_deploy(fake_home)
    bashrc = (fake_home / ".bashrc").read_text()
    assert bashrc.count(SENTINEL_OPEN) == 1, "re-runs must not duplicate the block"


def test_deploy_replaces_a_stale_block(fake_home: Path) -> None:
    """An older block between the same sentinels must be replaced, not appended."""
    install_stubs(fake_home)
    bashrc = fake_home / ".bashrc"
    bashrc.write_text(
        f"# existing user content\n"
        f"# {SENTINEL_OPEN}\n"
        f"echo OLD-AND-WRONG\n"
        f"# {SENTINEL_CLOSE}\n"
        f"# trailing user content\n"
    )
    run_deploy(fake_home)
    text = bashrc.read_text()
    assert "OLD-AND-WRONG" not in text
    assert text.count(SENTINEL_OPEN) == 1
    assert "# existing user content" in text
    assert "# trailing user content" in text


# ── Login-shell chain ─────────────────────────────────────────────────────


def test_deploy_warns_when_bash_profile_shadows_bashrc(fake_home: Path) -> None:
    """A ~/.bash_profile that does not source ~/.bashrc makes the block dead.

    bash reads the FIRST of ~/.bash_profile, ~/.bash_login, ~/.profile for a
    login shell. All three fleet boxes currently lack ~/.bash_profile, so the
    stock ~/.profile chain reaches ~/.bashrc — but creating one later would
    silently kill auto-attach with no other symptom.
    """
    install_stubs(fake_home)
    (fake_home / ".bash_profile").write_text("export PATH=$PATH:/opt/bin\n")
    result = run_deploy(fake_home)
    combined = (result.stdout + result.stderr).lower()
    assert "bash_profile" in combined or "warn" in combined


def test_deploy_quiet_about_chain_when_stock(fake_home: Path) -> None:
    install_stubs(fake_home)
    result = run_deploy(fake_home)
    assert "bash_profile" not in (result.stdout + result.stderr).lower()


# ── Timer hand-off ────────────────────────────────────────────────────────


def test_deploy_survives_timer_installer_failure(fake_home: Path) -> None:
    """The systemctl stub exits 1. A box with no systemd still gets tmux config."""
    install_stubs(fake_home)
    result = run_deploy(fake_home)
    assert result.returncode == 0, (
        "a failed timer install must not fail the whole deploy — "
        f"stderr: {result.stderr}"
    )
    assert (fake_home / ".tmux.conf").is_symlink()


# ── Physical root resolution (ext4 migration 2026-08-03) ──────────────────


def run_deploy_from(home: Path, script: Path) -> subprocess.CompletedProcess:
    bash = shutil.which("bash") or "/bin/bash"
    return subprocess.run(
        [bash, str(script)],
        env={"PATH": f"{stub_bin(home)}:/usr/bin:/bin", "HOME": str(home)},
        capture_output=True,
        text=True,
        timeout=90,
    )


def test_deploy_writes_the_physical_root_not_the_invoking_symlink(
    fake_home: Path, tmp_path: Path
) -> None:
    """The deploy script is the WRITER of the SSH login path, so whatever root
    it resolves becomes the fleet's landing directory until the next run.

    `pwd` is logical: invoked through a symlinked ancestor it reports the
    symlink, so a single run from the legacy `/mnt/local-analysis` path would
    silently rewrite the compatibility path back into ~/.bashrc and undo the
    migration. Only `pwd -P` is idempotent under either invocation path.
    """
    install_stubs(fake_home)
    legacy = tmp_path / "legacy-root"
    legacy.symlink_to(REPO_ROOT)

    result = run_deploy_from(fake_home, legacy / "scripts" / "setup" / "deploy-tmux.sh")
    assert result.returncode == 0, result.stderr

    bashrc = (fake_home / ".bashrc").read_text()
    assert str(REPO_ROOT.resolve()) in bashrc, (
        "sourcing line must name the physical repo root, got:\n" + bashrc
    )
    assert str(legacy) not in bashrc, (
        "sourcing line must not pin the symlink used to invoke the script"
    )
