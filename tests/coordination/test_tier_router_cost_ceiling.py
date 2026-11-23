"""Runtime cost-ceiling enforcement in the REAL tier router (#3205, acceptance #2).

These tests source the actual `scripts/coordination/routing/lib/tier_router.sh`
and call the real `route_by_tier` function (the executed path reached by both
route.sh and orchestrate.sh). `check_provider_available` is overridden per-test
to control availability; `route_by_tier` itself — candidate building, the
resolver filter, the emergency default, the JSON emit — is the real code.

Assertions are POSITIVE (which provider is selected), not merely "!= claude",
so a green run cannot be satisfied by the emergency fall-through alone (r1-F5).
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TIER_ROUTER = REPO_ROOT / "scripts" / "coordination" / "routing" / "lib" / "tier_router.sh"

STUBS = {
    "all": "check_provider_available() { return 0; }",
    "only_codex": 'check_provider_available() { [[ "$1" == codex ]]; }',
    "none": "check_provider_available() { return 1; }",
}


def _route(tier: str, context: str | None, stub: str) -> tuple[dict | None, int]:
    """Run the real route_by_tier; return (parsed_json_or_None, return_code)."""
    ctx_assign = f'ROUTE_CONTEXT="{context}" ' if context else ""
    script = f"""
set -o pipefail
source "{TIER_ROUTER}"
{STUBS[stub]}
out=$({ctx_assign}route_by_tier "{tier}" "" 0.9); rc=$?
printf '%s' "$out"
echo "__RC__=$rc"
"""
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    body, _, tail = r.stdout.rpartition("__RC__=")
    rc = int(tail.strip() or r.returncode)
    obj = json.loads(body) if body.strip() else None
    return obj, rc


def test_no_context_interactive_path_unchanged():
    # Baseline: COMPLEX primary is claude; with all providers available and no
    # context, claude is still selected (no regression to the interactive path).
    obj, rc = _route("COMPLEX", None, "all")
    assert rc == 0
    assert obj["provider"] == "claude"


def test_context_filters_claude_selects_next_available():
    # Same COMPLEX route under hermes_batch: claude is filtered; the next
    # available candidate (gemini) is chosen via the FILTER path, not emergency.
    obj, rc = _route("COMPLEX", "hermes_batch", "all")
    assert rc == 0
    assert obj["provider"] == "gemini"
    assert obj["provider"] != "claude"
    assert "Emergency" not in obj["reason"]
    assert obj["context"] == "hermes_batch"
    assert "claude" in obj["forbidden"]


def test_context_only_codex_available_selects_codex():
    # Proves CLI-token normalization end-to-end: with ONLY codex reachable, the
    # filtered route resolves to codex (not the openai-codex provider token).
    obj, rc = _route("COMPLEX", "hermes_batch", "only_codex")
    assert rc == 0
    assert obj["provider"] == "codex"


def test_emergency_default_under_ceiling_is_not_claude():
    # No provider reachable + ceiling context: emergency default must be the
    # context primary (codex), NEVER claude.
    obj, rc = _route("COMPLEX", "hermes_batch", "none")
    assert rc == 0
    assert obj["provider"] == "codex"
    assert obj["provider"] != "claude"
    assert "Emergency" in obj["reason"]


def test_unknown_context_fails_closed():
    # An explicit but invalid context aborts the route (rc 3) — never claude.
    obj, rc = _route("COMPLEX", "hermes-batch", "all")
    assert rc == 3
    assert obj is None
