"""Observed-behavior alignment checks for routing config (#1730)."""
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTING = REPO_ROOT / "config" / "agents" / "routing-config.yaml"
CAPS = REPO_ROOT / "config" / "agents" / "provider-capabilities.yaml"


def test_simple_and_standard_route_to_claude():
    with open(ROUTING) as handle:
        data = yaml.safe_load(handle)
    assert data["tiers"]["SIMPLE"]["primary"] == "claude"
    assert data["tiers"]["STANDARD"]["primary"] == "claude"


def test_research_and_data_dimensions_point_to_hermes():
    with open(ROUTING) as handle:
        data = yaml.safe_load(handle)
    assert data["dimensions"]["research_analysis"]["provider_signal"] == "hermes"
    assert data["dimensions"]["data_processing"]["provider_signal"] == "hermes"


def test_provider_capabilities_include_hermes_and_review_only_codex():
    with open(CAPS) as handle:
        data = yaml.safe_load(handle)
    assert "hermes" in data["providers"]
    assert "cross-review hard gate" in " ".join(data["providers"]["codex"]["primary_use_cases"]).lower()
