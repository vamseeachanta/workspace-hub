"""Cost-ceiling policy guard (#3192).

Asserts the DECLARED intent of routing-config.yaml's execution_contexts — NOT
runtime enforcement (the executed routers don't parse this file; see
docs/governance/2026-06-17-cost-ceiling-policy.md "Enforcement status").
"""
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING = REPO_ROOT / "config" / "agents" / "routing-config.yaml"
CAPS = REPO_ROOT / "config" / "agents" / "provider-capabilities.yaml"


def _routing():
    with open(ROUTING) as fh:
        return yaml.safe_load(fh)


def test_cost_ceiling_context_declares_forbid_claude():
    ctx = _routing()["execution_contexts"]
    for name, c in ctx.items():
        if c.get("cost_ceiling"):
            forbidden = c.get("forbid", [])
            assert "claude" in forbidden, f"{name} is cost_ceiling but does not forbid claude"
            assert "claude" != c.get("primary"), f"{name} cost-ceiling primary must not be claude"
            assert "claude" not in (c.get("fallbacks") or []), f"{name} cost-ceiling fallbacks must not include claude"


def test_hermes_context_primary_is_openai_codex():
    # Operator decision 2026-06-17: Hermes backing stays gpt-5.5/openai-codex.
    assert _routing()["execution_contexts"]["hermes_batch"]["primary"] == "openai-codex"


def test_hermes_context_fallback_is_gemini():
    # agy = the Antigravity Gemini CLI surface -> resolves to the `gemini` token.
    assert "gemini" in _routing()["execution_contexts"]["hermes_batch"]["fallbacks"]


def test_interactive_dev_primary_is_claude():
    assert _routing()["execution_contexts"]["interactive_dev"]["primary"] == "claude"


def test_cost_policy_reference_resolves():
    ref = _routing().get("cost_ceiling_policy")
    assert ref, "routing-config missing cost_ceiling_policy reference"
    doc = REPO_ROOT / ref
    assert doc.exists(), f"cost-ceiling policy doc missing: {ref}"
    text = doc.read_text().lower()
    assert "advisory only" in text, "policy doc must state the ceiling is advisory only"


def test_provider_caps_hermes_aligned():
    # provider-capabilities + routing-config must agree Hermes runs gpt-5.5.
    routing = _routing()
    with open(CAPS) as fh:
        caps = yaml.safe_load(fh)
    rc_primary = routing["agents"]["hermes"]["models"]["primary"]
    assert rc_primary == "gpt-5.5", f"routing-config hermes primary drifted: {rc_primary}"
    cap_primary = caps["providers"]["hermes"]["model_ids"]["primary"]
    assert cap_primary == "gpt-5.5", f"provider-capabilities hermes primary drifted: {cap_primary}"
