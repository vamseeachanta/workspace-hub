"""Unit + CLI tests for the single routing resolver (#3205).

The resolver is the ONE place execution-context forbid policy is interpreted.
These tests pin: forbid parsing, order-preserving filtering, CLI-token
normalization (openai-codex -> codex), fail-closed on unknown explicit context,
and the bash-facing CLI surface.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RESOLVER = REPO_ROOT / "scripts" / "ai" / "routing_resolver.py"

sys.path.insert(0, str(REPO_ROOT / "scripts" / "ai"))
import routing_resolver as rr  # noqa: E402


# --- pure API ---------------------------------------------------------------

def test_forbidden_providers_hermes_batch():
    assert rr.forbidden_providers("hermes_batch") == {"claude"}


def test_forbidden_providers_interactive_none():
    assert rr.forbidden_providers("interactive_dev") == set()


def test_filter_drops_claude_preserves_order():
    assert rr.filter_candidates(["claude", "codex", "gemini"], "hermes_batch") == ["codex", "gemini"]


def test_filter_no_context_passthrough():
    assert rr.filter_candidates(["claude", "codex"], None) == ["claude", "codex"]


def test_filter_unknown_context_fails_closed():
    # r2-C2: an explicit but unknown context must NOT pass claude through.
    with pytest.raises(rr.UnknownContextError):
        rr.filter_candidates(["claude"], "hermes-batch")  # typo (hyphen)


def test_filter_all_forbidden_falls_to_context_chain():
    # Only claude offered under a ceiling context -> fall to the context chain.
    assert rr.filter_candidates(["claude"], "hermes_batch") == ["codex", "gemini"]


def test_filter_no_fallback_returns_empty_when_all_forbidden():
    # provider_filter semantics: report genuine availability, do not re-add.
    assert rr.filter_candidates(["claude"], "hermes_batch", fallback=False) == []
    # non-forbidden survivors are still kept under no-fallback.
    assert rr.filter_candidates(["claude", "codex"], "hermes_batch", fallback=False) == ["codex"]


def test_chain_is_cli_normalized():
    # r2-C3/r1-F4: openai-codex (provider token) -> codex (CLI token).
    chain = rr.context_chain("hermes_batch")
    assert "openai-codex" not in chain
    assert chain == ["codex", "gemini"]


def test_cli_helper_normalizes():
    assert rr.cli("openai-codex") == "codex"
    assert rr.cli("claude") == "claude"


def test_cli_helper_normalizes_full_token_space():
    # review r3-F3: a forbid authored in provider tokens must not fail open.
    assert rr.cli("anthropic") == "claude"
    assert rr.cli("copilot") == "gemini"


def test_is_cost_ceiling_true_false():
    assert rr.is_cost_ceiling("hermes_batch") is True
    assert rr.is_cost_ceiling("interactive_dev") is False


# --- CLI surface (bash-facing) ----------------------------------------------

def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RESOLVER), *args],
        capture_output=True, text=True,
    )


def test_cli_filter_mode():
    r = _run("--context", "hermes_batch", "--filter", "claude,codex,gemini")
    assert r.returncode == 0
    assert r.stdout.split() == ["codex", "gemini"]


def test_cli_chain_mode():
    r = _run("--context", "hermes_batch", "--chain")
    assert r.returncode == 0
    assert r.stdout.split() == ["codex", "gemini"]


def test_cli_forbidden_mode():
    r = _run("--context", "hermes_batch", "--forbidden")
    assert r.returncode == 0
    assert r.stdout.split() == ["claude"]


def test_cli_unknown_context_exits_3():
    # r2-C2: fail closed at the CLI boundary too.
    r = _run("--context", "hermes-batch", "--filter", "claude,codex")
    assert r.returncode == 3
    assert "claude" not in r.stdout  # nothing usable emitted on stdout


def test_cli_empty_filter_is_empty_not_blank_string():
    # r1-F7: `--filter ""` must parse to [] (-> context chain), never a "" candidate.
    r = _run("--context", "hermes_batch", "--filter", "")
    assert r.returncode == 0
    assert "" not in r.stdout.split()
    # empty input -> context chain
    assert r.stdout.split() == ["codex", "gemini"]


def test_cli_forbidden_unknown_context_fails_closed():
    # review r3-F1: --forbidden must fail closed on an unknown context, like the
    # other modes (was the one mode that exited 0).
    r = _run("--context", "hermes-batch", "--forbidden")
    assert r.returncode == 3


def test_cli_chain_unknown_context_fails_closed():
    r = _run("--context", "nope", "--chain")
    assert r.returncode == 3


def test_cli_json_mode():
    r = _run("--context", "hermes_batch", "--json")
    assert r.returncode == 0
    obj = json.loads(r.stdout)
    assert obj["cost_ceiling"] is True
    assert obj["primary_cli"] == "codex"
    assert "claude" in obj["forbid_cli"]


# --- tier routing (#3209) ---------------------------------------------------

def test_tier_chain_simple_cost_aligned():
    assert rr.tier_chain("SIMPLE") == ["codex", "gemini", "claude"]


def test_tier_chain_standard_cost_aligned():
    assert rr.tier_chain("STANDARD") == ["codex", "claude", "gemini"]


def test_tier_chain_complex_claude_primary():
    assert rr.tier_chain("COMPLEX") == ["claude", "gemini", "codex"]


def test_tier_chain_has_no_hermes():
    # hermes is dropped from tier chains (routes via dimensions/contexts).
    for tier in rr.KNOWN_TIERS:
        assert "hermes" not in rr.tier_chain(tier)


def test_tier_chain_cli_normalized():
    for tier in rr.KNOWN_TIERS:
        assert "openai-codex" not in rr.tier_chain(tier)


def test_tier_unknown_raises():
    with pytest.raises(rr.UnknownTierError):
        rr.tier_chain("BOGUS")


def test_cli_tier_mode():
    r = _run("--tier", "SIMPLE")
    assert r.returncode == 0
    assert r.stdout.split() == ["codex", "gemini", "claude"]


def test_cli_tier_unknown_fails_closed():
    r = _run("--tier", "BOGUS")
    assert r.returncode == 3


def test_cli_all_tiers_json():
    r = _run("--all-tiers")
    assert r.returncode == 0
    obj = json.loads(r.stdout)
    assert set(obj) == set(rr.KNOWN_TIERS)
    assert obj["SIMPLE"][0] == "codex"
    assert obj["COMPLEX"][0] == "claude"


def test_cli_tier_with_context_rejected():
    # review r3-F4: tier modes don't take --context (no forbid in tier routing).
    r = _run("--tier", "SIMPLE", "--context", "hermes_batch")
    assert r.returncode != 0


def test_cli_emit_bash_table():
    r = _run("--emit-bash-table")
    assert r.returncode == 0
    assert 'declare -A TIER_PRIMARY=(' in r.stdout
    assert '[SIMPLE]="codex"' in r.stdout


def test_config_path_override_reads_yaml_at_runtime(tmp_path):
    # r1-F2: proves the resolver reads the YAML at runtime (single-source), via a
    # temp config where SIMPLE primary is flipped to gemini.
    cfg = tmp_path / "routing-config.yaml"
    cfg.write_text(
        "tiers:\n"
        "  SIMPLE: {primary: gemini, fallbacks: [codex]}\n"
        "  STANDARD: {primary: codex, fallbacks: [claude]}\n"
        "  COMPLEX: {primary: claude, fallbacks: [codex]}\n"
        "  REASONING: {primary: claude, fallbacks: [codex]}\n"
    )
    r = subprocess.run(
        [sys.executable, str(RESOLVER), "--tier", "SIMPLE"],
        capture_output=True, text=True, env={**os.environ, "ROUTING_CONFIG_PATH": str(cfg)},
    )
    assert r.returncode == 0
    assert r.stdout.split()[0] == "gemini"
