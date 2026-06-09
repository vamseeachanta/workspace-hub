"""WF0 (#3001): licensed-win-1/2 renamed to ace-win-1/2 with old names preserved as
hostname_aliases. Locks the alias-back-compat contract the whole rename rests on — every
fleet consumer resolves a machine via `[hostname] + hostname_aliases`, so the old identifiers
must keep resolving to the new canonical entry.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "config" / "workstations" / "registry.yaml"
HARNESS_CONFIG = REPO_ROOT / "scripts" / "readiness" / "harness-config.yaml"


def _machines() -> dict:
    return yaml.safe_load(REGISTRY.read_text())["machines"]


def _resolve(machines: dict, ident: str) -> str | None:
    """The fleet's canonical resolver idiom: match against hostname + hostname_aliases."""
    ident_l = ident.lower()
    for key, m in machines.items():
        candidates = [key, m.get("hostname", "")] + list(m.get("hostname_aliases") or [])
        if ident_l in [str(c).lower() for c in candidates]:
            return key
    return None


def test_canonical_keys_are_ace_win():
    machines = _machines()
    assert "ace-win-1" in machines, "ace-win-1 must be the canonical registry key"
    assert "ace-win-2" in machines
    # Old names must NOT remain as top-level keys (they moved to hostname_aliases).
    assert "licensed-win-1" not in machines
    assert "licensed-win-2" not in machines
    assert machines["ace-win-1"]["hostname"] == "ace-win-1"
    assert machines["ace-win-2"]["hostname"] == "ace-win-2"


def test_old_identifiers_preserved_as_aliases():
    machines = _machines()
    aliases1 = machines["ace-win-1"].get("hostname_aliases") or []
    aliases2 = machines["ace-win-2"].get("hostname_aliases") or []
    # The old logical name + the real Windows computer names survive as aliases.
    assert "licensed-win-1" in aliases1
    assert "ACMA-ANSYS05" in aliases1 and "acma-ansys05" in aliases1
    assert "licensed-win-2" in aliases2
    assert "acma-ws014" in aliases2


def test_old_identifiers_resolve_to_new_entry():
    machines = _machines()
    # Back-compat: any old reference still routes to the renamed canonical entry.
    assert _resolve(machines, "licensed-win-1") == "ace-win-1"
    assert _resolve(machines, "ACMA-ANSYS05") == "ace-win-1"
    assert _resolve(machines, "licensed-win-2") == "ace-win-2"
    assert _resolve(machines, "acma-ws014") == "ace-win-2"
    # And the new names resolve to themselves.
    assert _resolve(machines, "ace-win-1") == "ace-win-1"
    assert _resolve(machines, "ace-win-2") == "ace-win-2"


def test_harness_config_renamed_and_report_paths_follow():
    cfg = yaml.safe_load(HARNESS_CONFIG.read_text())
    machines = cfg["workstations"]
    assert "ace-win-1" in machines and "ace-win-2" in machines
    assert "licensed-win-1" not in machines and "licensed-win-2" not in machines
    assert machines["ace-win-1"]["report_path"].endswith("harness-readiness-ace-win-1.yaml")
    assert machines["ace-win-2"]["report_path"].endswith("harness-readiness-ace-win-2.yaml")
