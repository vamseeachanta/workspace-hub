"""Cost-ceiling coverage for the other two executed surfaces (#3205).

r1-F1: orchestrate.sh is a second caller of route_by_tier — driven end-to-end
       here with --context to prove claude is excluded.
r1-F2: provider_filter.sh::filter_available_providers unconditionally re-added
       claude — driven here to prove the ceiling removes it.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ORCHESTRATE = REPO_ROOT / "scripts" / "coordination" / "routing" / "orchestrate.sh"
PROVIDER_FILTER = REPO_ROOT / "scripts" / "coordination" / "routing" / "lib" / "provider_filter.sh"
RESOLVER = REPO_ROOT / "scripts" / "ai" / "routing_resolver.py"

_USAGE = json.dumps({"requests_percent": 5, "tokens_percent": 5,
                     "cost_today": 1, "daily_budget": 100})


# --- r1-F1: orchestrate.sh end-to-end ---------------------------------------

def _orchestrate(*args: str) -> str:
    r = subprocess.run(["bash", str(ORCHESTRATE), *args],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout


def _available_line(out: str) -> str:
    m = re.search(r"Available providers: (\[.*\])", out)
    return m.group(1) if m else ""


def _routed(out: str) -> str:
    m = re.search(r"Routed to: (\S+)", out)
    return m.group(1) if m else ""


def test_orchestrate_with_context_excludes_claude():
    out = _orchestrate("--context", "hermes_batch",
                       "design a complex multi-file architecture refactor")
    assert "claude" not in _available_line(out)
    assert _routed(out) != "claude"


def test_orchestrate_without_context_can_include_claude():
    # Baseline: without the ceiling, claude is an available provider (proves the
    # exclusion above is the ceiling's doing, not an unrelated availability gap).
    out = _orchestrate("design a complex multi-file architecture refactor")
    assert "claude" in _available_line(out)


# --- r1-F2: provider_filter.sh ----------------------------------------------

def _filter_available(tmp_path: Path, context: str | None) -> list[str]:
    for prov in ("codex", "gemini", "claude"):
        (tmp_path / f"{prov}_usage.json").write_text(_USAGE)
    ctx_assign = f'ROUTE_CONTEXT="{context}" ' if context else ""
    script = f"""
set -o pipefail
export CONFIG_DIR="{tmp_path}"
export RESOLVER="{RESOLVER}"
source "{PROVIDER_FILTER}"
{ctx_assign}filter_available_providers
"""
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def test_provider_filter_drops_claude_under_context(tmp_path):
    avail = _filter_available(tmp_path, "hermes_batch")
    assert "claude" not in avail
    assert "codex" in avail and "gemini" in avail


def test_provider_filter_keeps_claude_without_context(tmp_path):
    avail = _filter_available(tmp_path, None)
    assert "claude" in avail


def test_provider_filter_unknown_context_fails_closed(tmp_path):
    # review r3-F2: a bad context must fail closed even on the empty-available path.
    for prov in ("codex", "gemini", "claude"):
        (tmp_path / f"{prov}_usage.json").write_text(_USAGE)
    script = f"""
set -o pipefail
export CONFIG_DIR="{tmp_path}"
export RESOLVER="{RESOLVER}"
source "{PROVIDER_FILTER}"
ROUTE_CONTEXT="hermes-batch" filter_available_providers
"""
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
    assert r.returncode == 3
