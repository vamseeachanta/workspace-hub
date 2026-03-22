"""
Tests for WRK-5110: work-queue-orchestrator folder-skill.
  - generate-stage-mapping.py produces canonical 20-stage mapping
  - hooks.yaml and hooks-schema.yaml are valid YAML
  - SKILL.md is lean (<50 lines)
  - scripts/ contains no stage-specific files
Run: uv run --no-project python -m pytest tests/work-queue/test_stage_mapping.py -v
"""

import os
import subprocess
import sys

import pytest
import yaml

REPO = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
ORCH_DIR = os.path.join(
    REPO, ".claude", "skills", "workspace-hub", "work-queue-orchestrator"
)
REFS_DIR = os.path.join(ORCH_DIR, "references")
SCRIPTS_DIR = os.path.join(ORCH_DIR, "scripts")
STAGE_CONTRACTS = os.path.join(REPO, "scripts", "work-queue", "stages")


# ── generate-stage-mapping.py tests ─────────────────────────────────────


class TestGenerateStageMapping:
    """Canonical stage mapping generation."""

    @pytest.fixture(scope="class")
    def mapping_output(self):
        script = os.path.join(SCRIPTS_DIR, "generate-stage-mapping.py")
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        return yaml.safe_load(result.stdout)

    def test_produces_20_stages(self, mapping_output):
        """Mapping must contain exactly 20 stage entries."""
        assert len(mapping_output["stages"]) == 20

    def test_stage_numbers_sequential(self, mapping_output):
        """Stage orders must be 1 through 20."""
        orders = [s["order"] for s in mapping_output["stages"]]
        assert orders == list(range(1, 21))

    def test_names_match_contracts(self, mapping_output):
        """Each stage name must match its contract YAML name field."""
        for entry in mapping_output["stages"]:
            contract_path = os.path.join(REPO, entry["contract"])
            with open(contract_path) as f:
                contract = yaml.safe_load(f)
            assert entry["name"] == contract["name"], (
                f"Stage {entry['order']}: mapping name '{entry['name']}' "
                f"!= contract name '{contract['name']}'"
            )

    def test_output_valid_yaml(self, mapping_output):
        """Mapping output must be parseable YAML with 'stages' key."""
        assert "stages" in mapping_output
        assert isinstance(mapping_output["stages"], list)

    def test_required_fields_present(self, mapping_output):
        """Each stage entry must have required fields."""
        required = {
            "order", "name", "slug", "contract",
            "micro_skill", "weight", "human_gate", "invocation",
        }
        for entry in mapping_output["stages"]:
            missing = required - set(entry.keys())
            assert not missing, (
                f"Stage {entry.get('order', '?')}: missing {missing}"
            )


# ── stage-mapping.yaml reference artifact ────────────────────────────────


class TestStageMappingArtifact:
    """The generated reference file must exist and be valid."""

    def test_stage_mapping_yaml_exists(self):
        path = os.path.join(REFS_DIR, "stage-mapping.yaml")
        assert os.path.isfile(path), "references/stage-mapping.yaml missing"

    def test_stage_mapping_yaml_has_20_stages(self):
        path = os.path.join(REFS_DIR, "stage-mapping.yaml")
        with open(path) as f:
            data = yaml.safe_load(f)
        assert len(data["stages"]) == 20


# ── hooks.yaml and hooks-schema.yaml ─────────────────────────────────────


class TestHooksFiles:
    """hooks.yaml and hooks-schema.yaml must be valid YAML."""

    def test_hooks_yaml_valid(self):
        path = os.path.join(ORCH_DIR, "hooks.yaml")
        assert os.path.isfile(path), "hooks.yaml missing"
        with open(path) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)
        assert "constraints" in data, "hooks.yaml must have 'constraints' key"

    def test_hooks_schema_valid_yaml(self):
        path = os.path.join(REFS_DIR, "hooks-schema.yaml")
        assert os.path.isfile(path), "hooks-schema.yaml missing"
        with open(path) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)


# ── SKILL.md constraints ─────────────────────────────────────────────────


class TestSkillMd:
    """Orchestrator SKILL.md must be lean and well-formed."""

    def test_skill_md_exists(self):
        path = os.path.join(ORCH_DIR, "SKILL.md")
        assert os.path.isfile(path), "SKILL.md missing"

    def test_skill_md_under_50_lines(self):
        path = os.path.join(ORCH_DIR, "SKILL.md")
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) < 50, (
            f"SKILL.md has {len(lines)} lines, must be <50"
        )

    def test_skill_md_has_frontmatter(self):
        path = os.path.join(ORCH_DIR, "SKILL.md")
        with open(path) as f:
            content = f.read()
        assert content.startswith("---"), "SKILL.md must start with ---"
        assert content.count("---") >= 2, "SKILL.md must have closing ---"


# ── scripts/ directory constraints ───────────────────────────────────────


class TestScriptsDir:
    """scripts/ must contain only orchestrator-owned helpers."""

    def test_no_stage_specific_scripts(self):
        """No files named stage-NN-* should exist in scripts/."""
        if not os.path.isdir(SCRIPTS_DIR):
            pytest.skip("scripts/ dir not yet created")
        for name in os.listdir(SCRIPTS_DIR):
            assert not name.startswith("stage-"), (
                f"Stage-specific script '{name}' found in orchestrator scripts/"
            )
