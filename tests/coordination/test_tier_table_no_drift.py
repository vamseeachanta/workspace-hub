"""Drift-guard: the bash tier table is a faithful generation of the YAML (#3209).

The `tier_router.sh` `declare -A TIER_*` arrays are GENERATED from
routing-config.yaml tiers.* via `routing_resolver.py --emit-bash-table`. This
test fails CI if someone edits the YAML without regenerating the bash block (or
hand-edits the block), and asserts no hardcoded tier table lingers in route.sh.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RESOLVER = REPO_ROOT / "scripts" / "ai" / "routing_resolver.py"
TIER_ROUTER = REPO_ROOT / "scripts" / "coordination" / "routing" / "lib" / "tier_router.sh"
ROUTE_SH = REPO_ROOT / "scripts" / "coordination" / "routing" / "route.sh"
REPO_CONFIG = REPO_ROOT / "config" / "agents" / "routing-config.yaml"


def _generated_block() -> list[str]:
    # Pin the config to the repo's (ignore any ambient ROUTING_CONFIG_PATH) so the
    # guard always compares against the canonical source — review r3-F5.
    env = {**os.environ, "ROUTING_CONFIG_PATH": str(REPO_CONFIG)}
    r = subprocess.run([sys.executable, str(RESOLVER), "--emit-bash-table"],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return [ln.strip() for ln in r.stdout.strip().splitlines()]


def _committed_block() -> list[str]:
    text = TIER_ROUTER.read_text()
    m = re.search(r">>> GENERATED.*?\n(.*?)# <<< END GENERATED", text, re.DOTALL)
    assert m, "GENERATED marker block not found in tier_router.sh"
    return [ln.strip() for ln in m.group(1).strip().splitlines()
            if ln.strip().startswith("declare -A")]


def test_committed_bash_table_matches_resolver():
    assert _committed_block() == _generated_block()


def test_route_sh_has_no_hardcoded_tier_table():
    # The --config display must render live from the resolver, not hardcode tiers.
    text = ROUTE_SH.read_text()
    assert "_resolver --all-tiers" in text
    # No hardcoded "SIMPLE -> codex"/"SIMPLE    -> codex" style rows remain.
    assert not re.search(r'echo\s+"\s*SIMPLE\s+->', text)
