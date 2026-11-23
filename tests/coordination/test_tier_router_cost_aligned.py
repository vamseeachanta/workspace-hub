"""Cost-aligned tier routing in the REAL router (#3209).

Drives the actual `route_by_tier` (the generated bash table) and asserts cheap
tiers route to codex, not claude — and that it composes with the #3205 cost
ceiling.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TIER_ROUTER = REPO_ROOT / "scripts" / "coordination" / "routing" / "lib" / "tier_router.sh"

ALL_AVAILABLE = "check_provider_available() { return 0; }"


def _route(tier: str, context: str | None = None, stub: str = ALL_AVAILABLE) -> tuple[dict | None, int]:
    ctx = f'ROUTE_CONTEXT="{context}" ' if context else ""
    script = f"""
set -o pipefail
source "{TIER_ROUTER}"
{stub}
out=$({ctx}route_by_tier "{tier}" "" 0.9); rc=$?
printf '%s' "$out"
echo "__RC__=$rc"
"""
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    body, _, tail = r.stdout.rpartition("__RC__=")
    rc = int(tail.strip() or r.returncode)
    return (json.loads(body) if body.strip() else None), rc


def test_simple_routes_to_codex():
    obj, rc = _route("SIMPLE")
    assert rc == 0
    assert obj["provider"] == "codex"
    assert obj["provider"] != "claude"


def test_standard_routes_to_codex():
    obj, rc = _route("STANDARD")
    assert rc == 0
    assert obj["provider"] == "codex"


def test_complex_routes_to_claude():
    obj, rc = _route("COMPLEX")
    assert rc == 0
    assert obj["provider"] == "claude"


def test_reasoning_routes_to_claude():
    obj, rc = _route("REASONING")
    assert rc == 0
    assert obj["provider"] == "claude"


def test_simple_under_ceiling_still_codex():
    # Composes with #3205: SIMPLE primary is already codex; under hermes_batch,
    # claude is filtered from the fallback and codex remains.
    obj, rc = _route("SIMPLE", context="hermes_batch")
    assert rc == 0
    assert obj["provider"] == "codex"
    assert obj["provider"] != "claude"
