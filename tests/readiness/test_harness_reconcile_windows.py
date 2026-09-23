"""WF1 (#2999) — OS-aware `_base` + Windows portability for the role-overlay reconciler.

The reconciler now selects a per-OS deny subset (`_base.deny_required_os[<machine os>]`) on top of
the universal `_base.deny_required`, driven by the target machine's registry `os` field. These tests
load the REAL config so they double as a regression lock: the composed deny-set for a Linux machine
must stay byte-identical to the pre-WF1 flat 37-entry `_base` (a1/a2 are already converged — any
change would re-trigger live drift).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "scripts" / "readiness" / "harness_reconcile.py"
ROLES_CFG = REPO / "config" / "workstations" / "harness-roles.yaml"
REGISTRY = REPO / "config" / "workstations" / "registry.yaml"

spec = importlib.util.spec_from_file_location("harness_reconcile", MOD)
hr = importlib.util.module_from_spec(spec)
sys.modules["harness_reconcile"] = hr
spec.loader.exec_module(hr)

# Frozen pre-WF1 flat `_base` deny-list (37 entries). The Linux compose MUST equal this exactly.
FROZEN_LINUX_37 = {
    "Bash(rm -rf /)", "Bash(rm -rf ~:*)", "Bash(rm -rf .:*)",
    "Bash(dd if=/dev/zero:*)", "Bash(mkfs:*)", "Bash(shred:*)",
    "Bash(sudo:*)", "Bash(su :*)", "Bash(pkexec:*)", "Bash(doas:*)",
    "Bash(chmod 777:*)", "Bash(eval:*)", "Bash(sh -c:*)", "Bash(bash -c:*)",
    "Bash(zsh -c:*)", "Bash(python -c:*)", "Bash(python3 -c:*)", "Bash(perl -e:*)",
    "Bash(ruby -e:*)", "Bash(node -e:*)", "Bash(curl * | bash:*)", "Bash(curl * | sh:*)",
    "Bash(wget * -O- | bash:*)", "Bash(wget * -O- | sh:*)", "Bash(| bash:*)", "Bash(| sh:*)",
    "Bash(nc:*)", "Bash(ncat:*)", "Bash(base64:*)", "Bash(xxd:*)",
    "Bash(git push --force:*)", "Bash(git push -f:*)", "Bash(git push --force-with-lease:*)",
    "Bash(git -c core.hooksPath:*)", "Bash(git -c core.hookspath:*)",
    "Bash(crontab:*)", "Bash(systemctl:*)",
}
LINUX_ONLY = {"Bash(crontab:*)", "Bash(systemctl:*)", "Bash(sudo:*)", "Bash(pkexec:*)", "Bash(doas:*)"}


@pytest.fixture(scope="module")
def cfg():
    return yaml.safe_load(ROLES_CFG.read_text())


@pytest.fixture(scope="module")
def registry():
    return yaml.safe_load(REGISTRY.read_text())["machines"]


def test_linux_compose_equals_frozen_37(cfg):
    """Behavior-preserving: a Linux machine still gets exactly the pre-WF1 37-entry set."""
    ov = hr.compose_overlay(cfg, ["control-plane"], machine_os="linux")
    assert set(ov["deny_required"]) == FROZEN_LINUX_37


def test_windows_compose_has_universal_and_windows_not_nix(cfg):
    ov = hr.compose_overlay(cfg, ["licensed-solver"], machine_os="windows")
    deny = set(ov["deny_required"])
    # universal guards still present (Git-Bash dangers)
    assert "Bash(rm -rf /)" in deny and "Bash(curl * | bash:*)" in deny
    # windows-specific destructive guards present
    assert "Bash(format:*)" in deny and "Bash(reg delete:*)" in deny and "Bash(diskpart:*)" in deny
    # *nix-only entries absent on Windows
    assert not (LINUX_ONLY & deny), f"linux-only leaked onto windows: {LINUX_ONLY & deny}"


def test_macos_compose_subset(cfg):
    ov = hr.compose_overlay(cfg, ["licensed-solver"], machine_os="macos")
    deny = set(ov["deny_required"])
    assert "Bash(rm -rf /)" in deny           # universal
    assert "Bash(sudo:*)" in deny             # mac has sudo
    assert "Bash(systemctl:*)" not in deny    # mac has no systemd
    assert "Bash(format:*)" not in deny       # not a windows host


def test_deny_required_os_key_is_popped(cfg):
    """The config-only OS map must never survive into the composed overlay / settings."""
    for os_name in ("linux", "windows", "macos", None):
        ov = hr.compose_overlay(cfg, ["licensed-solver"], machine_os=os_name)
        assert "deny_required_os" not in ov


def test_ace_win_now_managed(registry):
    assert hr.is_managed(registry["ace-win-1"]["harness_profile"]) is True
    assert hr.is_managed(registry["ace-win-2"]["harness_profile"]) is True


def test_resolve_machine_id_via_alias_and_hostname(registry):
    """Every alias a machine declares must resolve to that machine, in any case.

    Asserted as a property over `hostname_aliases` rather than against pinned literals:
    registry.yaml is the SSOT for which identifiers a machine answers to (a real Windows
    computer name is declared there so host detection resolves), and this test must keep
    testing the resolver, not a copy of the registry's current contents.
    """
    for mid in ("ace-win-1", "ace-win-2"):
        aliases = registry[mid].get("hostname_aliases") or []
        assert aliases, f"{mid} must declare at least one back-compat alias"
        for alias in aliases:
            assert hr.resolve_machine_id(registry, alias) == mid
            # Windows reports hostnames upper-case; resolution must be case-insensitive.
            assert hr.resolve_machine_id(registry, str(alias).upper()) == mid
    assert hr.resolve_machine_id(registry, "licensed-win-1") == "ace-win-1"   # WF0 back-compat alias
    assert hr.resolve_machine_id(registry, "ace-win-1") == "ace-win-1"        # new hostname
    assert hr.resolve_machine_id(registry, "ace-linux-1") == "dev-primary"    # linux hostname
    assert hr.resolve_machine_id(registry, "nope-host") is None


def test_detect_live_daemons_is_windows_safe():
    """A host without pgrep (Windows) must report no daemons, not crash."""
    def _no_pgrep(_pat):
        raise FileNotFoundError("pgrep")  # simulate pgrep absent
    assert hr.detect_live_daemons(pgrep_fn=_no_pgrep) == []
