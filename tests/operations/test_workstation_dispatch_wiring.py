# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Wiring tests for workstation-dispatch.sh F3 additions (#2970).

Covers the three additive flags wired into the live dispatcher without changing
its default behavior:

  * --route <task_type>  -> prints provider routing for the selected machine via
                            scripts/ai/provider_route.py (informational only).
  * --role-aware         -> honors task roles ∩ machine harness_profile.roles via
                            scripts/operations/dispatch_select.py, IN ADDITION to
                            the existing requires match (default OFF).
  * --lease              -> acquires an atomic git-ref lease (dispatch_lease.py +
                            git_ref_lease.py) before dispatching; aborts if held
                            (default OFF).

Hermetic: every test uses --dry-run (no SSH / no execution) except the lease
tests, which run against a throwaway temp git repo via WS_DISPATCH_LEASE_REPO and
never SSH (the selected machine resolves local on the dev host, or the lease is
acquired before any execution and asserted directly).
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "operations" / "workstation-dispatch.sh"

# A task that exists in config/scheduled-tasks/schedule-tasks.yaml.
KNOWN_TASK = "gsd-researcher"
# A known policy task_type (key in config/ai-tools/provider-routing-policy.yaml roles).
KNOWN_TASK_TYPE = "review"


def _run(args, env=None, cwd=REPO_ROOT):
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=full_env,
        timeout=180,
    )


def test_bash_syntax_ok():
    """(a) `bash -n` must pass on the dispatcher."""
    r = subprocess.run(
        ["bash", "-n", str(SCRIPT)], capture_output=True, text=True
    )
    assert r.returncode == 0, r.stderr


def test_existing_dry_run_task_no_regression():
    """(c) Existing `--dry-run --task <id>` still works (no regression)."""
    r = _run(["--task", KNOWN_TASK, "--dry-run"])
    assert r.returncode == 0, r.stderr
    assert "DRY RUN" in r.stdout
    # No F3 informational lines leak into the default path.
    assert "Provider routing" not in r.stdout
    assert "dispatch lease" not in r.stdout.lower()


def test_route_prints_nonempty_provider_list():
    """(b) `--route <task_type>` prints a non-empty provider list (dry-run)."""
    r = _run(["--task", KNOWN_TASK, "--route", KNOWN_TASK_TYPE, "--dry-run"])
    assert r.returncode == 0, r.stderr
    assert "Provider routing" in r.stdout
    # The routing line lists at least one provider after the colon.
    route_lines = [ln for ln in r.stdout.splitlines() if "Provider routing" in ln]
    assert route_lines, r.stdout
    after_colon = route_lines[0].rsplit("):", 1)[-1].strip()
    assert after_colon, f"empty provider list in: {route_lines[0]!r}"
    assert "<none" not in after_colon


def test_route_does_not_change_selected_machine():
    """--route is informational: same target with and without it."""
    base = _run(["--task", KNOWN_TASK, "--dry-run"])
    routed = _run(["--task", KNOWN_TASK, "--route", KNOWN_TASK_TYPE, "--dry-run"])
    assert base.returncode == 0 and routed.returncode == 0

    def target(out):
        for ln in out.splitlines():
            if ln.startswith("[dispatch] Target:"):
                return ln
        return None

    assert target(base.stdout) == target(routed.stdout)


def test_role_aware_selects_a_machine_no_regression():
    """`--role-aware --dry-run` still resolves a target (role ∩ requires)."""
    r = _run(["--task", "equality-report", "--role-aware", "--dry-run"])
    assert r.returncode == 0, r.stderr
    assert "DRY RUN" in r.stdout
    assert any(ln.startswith("[dispatch] Target:") for ln in r.stdout.splitlines())


def test_unknown_flag_still_rejected():
    """Arg parser still rejects unknown flags (additive change kept the guard)."""
    r = _run(["--task", KNOWN_TASK, "--bogus"])
    assert r.returncode != 0
    assert "unknown arg" in r.stderr


# ── Lease tests: hermetic temp git repo via WS_DISPATCH_LEASE_REPO ───────────

@pytest.fixture()
def temp_git_repo(tmp_path):
    repo = tmp_path / "lease-repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-q", "--allow-empty", "-m", "init"],
        check=True,
    )
    yield repo


def _lease_refs(repo: Path):
    r = subprocess.run(
        ["git", "-C", str(repo), "show-ref"], capture_output=True, text=True
    )
    return [ln for ln in r.stdout.splitlines() if "dispatch/leases/" in ln]


def _machine_is_local() -> bool:
    """True iff a registry machine resolves to this host (so --command runs local
    rather than attempting SSH). Skips lease-execution tests on detached hosts."""
    host = subprocess.run(
        ["hostname", "-s"], capture_output=True, text=True
    ).stdout.strip().lower()
    return host in {"ace-linux-1", "ace-linux-2"}


@pytest.mark.skipif(
    not _machine_is_local(),
    reason="lease+execute path needs a registry-local host (no SSH in tests)",
)
def test_lease_acquire_run_release(temp_git_repo):
    """--lease acquires before running a local echo, then releases (ref gone)."""
    r = _run(
        ["--machine", "dev-primary", "--command", "echo LEASE_OK", "--lease"],
        env={"WS_DISPATCH_LEASE_REPO": str(temp_git_repo)},
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "Lease acquired" in r.stdout
    assert "LEASE_OK" in r.stdout
    assert "released" in r.stdout
    # Net-clean: no lease ref remains after a clean release.
    assert _lease_refs(temp_git_repo) == []


def test_lease_aborts_when_held(temp_git_repo):
    """A pre-held lease for the same name causes a clear abort (no double-run),
    and the foreign holder's lease is NOT stolen or deleted."""
    cmd = "echo SHOULD_NOT_RUN"
    # Compute the lease name the script will use: cmd-<cksum>.
    cksum = subprocess.run(
        ["cksum"], input=cmd, capture_output=True, text=True
    ).stdout.split()[0]
    name = f"cmd-{cksum}"

    # Pre-hold the lease as a different holder via the real cores.
    pre = subprocess.run(
        [
            "uv", "run", "--no-project", "python", "-c",
            (
                "import os,sys,time\n"
                "sys.path.insert(0,'scripts/operations')\n"
                "from git_ref_lease import GitRefLease\n"
                "import dispatch_lease as dl\n"
                "g=GitRefLease(os.environ['R'])\n"
                "b=dl.acquire(g,os.environ['N'],'other-host',ttl_s=3600,"
                "now=time.time(),new_token='tok-other')\n"
                "print('preheld' if b else 'FAIL')\n"
            ),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "R": str(temp_git_repo), "N": name},
    )
    assert "preheld" in pre.stdout, pre.stderr

    r = _run(
        ["--machine", "dev-primary", "--command", cmd, "--lease"],
        env={"WS_DISPATCH_LEASE_REPO": str(temp_git_repo)},
    )
    assert r.returncode != 0
    assert "held by another dispatcher" in r.stderr
    assert "SHOULD_NOT_RUN" not in r.stdout  # command never executed
    # Foreign lease still present (token-fencing prevents theft/delete on abort).
    refs = _lease_refs(temp_git_repo)
    assert any(name in ln for ln in refs), refs


def test_lease_requires_git_repo(tmp_path):
    """--lease with a non-git lease repo fails closed with a clear message."""
    non_git = tmp_path / "not-a-repo"
    non_git.mkdir()
    r = _run(
        ["--machine", "dev-primary", "--command", "echo X", "--lease"],
        env={"WS_DISPATCH_LEASE_REPO": str(non_git)},
    )
    assert r.returncode != 0
    assert "requires a git repo" in r.stderr


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
