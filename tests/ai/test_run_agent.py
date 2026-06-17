"""Tests for scripts/ai/run_agent.py (G1 / #3116 — portable bounded-worker invocation).

The deterministic core under test (NOT the slow 3-provider behavioral oracle):
  - load a portable *.agent.yaml definition
  - resolve its logical capabilities against the capability_bindings in
    config/agents/provider-capabilities.yaml, per provider, into
    {enforced, advisory, unsupported}
  - FAIL CLOSED before any dispatch if a requested capability is `unsupported`
    on the target provider (the plan's mandated negative test)
  - emit a run manifest (prompt_hash, enforcement labels, advisory/unsupported,
    provider, wrapper) so a run is auditable

Module is loaded by file path via importlib (mirrors test_provider_route.py).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "run_agent.py"
spec = importlib.util.spec_from_file_location("run_agent", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["run_agent"] = module
spec.loader.exec_module(module)

load_agent_def = module.load_agent_def
load_bindings = module.load_bindings
resolve_capabilities = module.resolve_capabilities
build_manifest = module.build_manifest
prepare_run = module.prepare_run
UnsupportedCapabilityError = module.UnsupportedCapabilityError

REVIEWER_DEF = REPO_ROOT / "config" / "agents" / "agent-defs" / "reviewer.agent.yaml"
UNSUPPORTED_FIXTURE = REPO_ROOT / "tests" / "ai" / "fixtures" / "needs_unsupported.agent.yaml"

# The real bindings block is the contract under test.
BINDINGS = load_bindings()


# --- definition loading -----------------------------------------------------

def test_reviewer_def_loads_with_required_fields():
    d = load_agent_def(REVIEWER_DEF)
    assert d["name"] == "reviewer"
    assert d["role"] == "worker"
    assert isinstance(d["prompt"], str) and d["prompt"].strip()
    assert isinstance(d["capabilities"], list) and d["capabilities"]


def test_every_reviewer_capability_is_bound():
    # Referential integrity: each declared capability must exist in bindings.
    d = load_agent_def(REVIEWER_DEF)
    for cap in d["capabilities"]:
        assert cap in BINDINGS, f"capability {cap!r} missing from capability_bindings"


# --- per-provider resolution ------------------------------------------------

def test_claude_resolves_capabilities_as_enforced():
    d = load_agent_def(REVIEWER_DEF)
    res = resolve_capabilities(d, "claude", BINDINGS)
    # reviewer's caps are enforceable on Claude (it accepts a tools: allowlist)
    assert res["enforced"], "expected enforced caps on claude"
    assert not res["unsupported"]
    # enforced caps carry their native Claude tool names
    assert all(res["native"].get(c) for c in res["enforced"])


def test_codex_resolves_capabilities_as_advisory():
    d = load_agent_def(REVIEWER_DEF)
    res = resolve_capabilities(d, "codex", BINDINGS)
    # Codex is a monolithic CLI: caps cannot be enforced, only advised
    assert res["advisory"], "expected advisory caps on codex"
    assert not res["enforced"]
    assert not res["unsupported"]


# --- fail-closed negative test (the plan's mandated guard) -------------------

def test_unsupported_capability_fails_closed_before_dispatch():
    d = load_agent_def(UNSUPPORTED_FIXTURE)
    with pytest.raises(UnsupportedCapabilityError):
        resolve_capabilities(d, "codex", BINDINGS)


def test_prepare_run_fails_closed_and_does_not_emit_dispatch():
    # prepare_run must raise BEFORE returning any dispatch spec
    with pytest.raises(UnsupportedCapabilityError):
        prepare_run(UNSUPPORTED_FIXTURE, "codex", bindings=BINDINGS)


# --- manifest ---------------------------------------------------------------

def test_manifest_has_audit_fields():
    d = load_agent_def(REVIEWER_DEF)
    m = build_manifest(d, "gemini", BINDINGS)
    assert m["agent"] == "reviewer"
    assert m["provider"] == "gemini"
    assert len(m["prompt_hash"]) == 64  # sha256 hex
    assert set(m["enforcement"]) == set(d["capabilities"])  # one label per cap
    assert "advisory" in m and "unsupported" in m
    assert m["wrapper"].endswith("submit-to-gemini.sh")


def test_prompt_hash_is_stable():
    d = load_agent_def(REVIEWER_DEF)
    a = build_manifest(d, "codex", BINDINGS)["prompt_hash"]
    b = build_manifest(d, "codex", BINDINGS)["prompt_hash"]
    assert a == b


def test_prepare_run_returns_manifest_and_dispatch_for_supported():
    manifest, dispatch = prepare_run(REVIEWER_DEF, "codex", bindings=BINDINGS)
    assert manifest["provider"] == "codex"
    assert dispatch["wrapper"].endswith("submit-to-codex.sh")
    # dispatch carries the materialized prompt (preamble + agent prompt)
    assert dispatch["prompt"].strip()


# --- #3190: skill routing + back-compat + agy fail-closed --------------------

def test_no_routed_skill_is_byte_identical_back_compat():
    # absence of a routed skill must leave the prompt exactly as before
    _, d_none = prepare_run(REVIEWER_DEF, "codex", bindings=BINDINGS, routed_skill=None)
    _, d_default = prepare_run(REVIEWER_DEF, "codex", bindings=BINDINGS)
    assert d_none["prompt"] == d_default["prompt"]
    assert "# Routed skill:" not in d_none["prompt"]


def test_routed_skill_is_prepended_and_recorded():
    manifest, dispatch = prepare_run(REVIEWER_DEF, "codex", bindings=BINDINGS,
                                     routed_skill="development/github/code-review")
    assert manifest["routed_skill"] == "development/github/code-review"
    assert "# Routed skill: development/github/code-review" in dispatch["prompt"]
    assert ".claude/skills/development/github/code-review/SKILL.md" in dispatch["prompt"]


def test_agy_is_unsupported_for_dispatch_fails_closed():
    # agy has no headless dispatch -> not a WRAPPERS/bindings provider -> every
    # capability resolves unsupported -> resolve_capabilities raises (no fake wrapper).
    d = load_agent_def(REVIEWER_DEF)
    with pytest.raises(UnsupportedCapabilityError):
        resolve_capabilities(d, "agy", BINDINGS)
