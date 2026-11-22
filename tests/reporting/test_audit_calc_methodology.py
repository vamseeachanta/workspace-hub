"""Synthetic structural audit tests; no engineering calculations or values.

Policy: issue #3687 specifies 16 sections. Section names and order come from
config/reporting/calculation-report-schema.yaml: required_fields followed by
optional_sections. Expectations below are independent of the audit implementation.
"""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "reporting" / "audit-calc-methodology.py"
SCHEMA = ROOT / "config" / "reporting" / "calculation-report-schema.yaml"


@pytest.fixture
def audit_module():
    spec = importlib.util.spec_from_file_location("audit_calc_methodology", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def checklist():
    """Read cited policy directly, without calling production checklist code."""
    schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
    names = list(schema["required_fields"]) + list(schema["optional_sections"])
    assert len(names) == 16  # Checklist size specified by issue #3687.
    assert len(set(names)) == len(names)
    return names


def write_yaml(tmp_path, content):
    path = tmp_path / "synthetic.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def run_cli(path, cwd):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def test_empty_mapping_scores_zero(audit_module, checklist, tmp_path):
    result = audit_module.audit_file(write_yaml(tmp_path, "{}\n"))
    assert result["present"] == []
    assert result["missing"] == checklist
    assert result["total"] == 16  # Issue #3687; schema checklist above.
    assert result["percentage"] == 0.0  # Hand calculation: 0 / 16 * 100.
    assert "presence is not engineering validation" in result["notice"].lower()


def test_complete_fixture_scores_full(audit_module, checklist, tmp_path):
    # Independently authored nonempty placeholders, deliberately not valid reports.
    content = """\
metadata: {description: synthetic}
inputs: [synthetic]
methodology: {description: synthetic}
outputs: [synthetic]
assumptions: [synthetic]
references: [synthetic]
charts: [synthetic]
data_tables: [synthetic]
scope: {description: synthetic}
design_basis: {description: synthetic}
materials: [synthetic]
calculations: [synthetic]
sensitivity: [synthetic]
validation: {description: synthetic}
verification: {description: synthetic}
conclusions: {description: synthetic}
"""
    result = audit_module.audit_file(write_yaml(tmp_path, content))
    assert result["present"] == checklist
    assert result["missing"] == []
    assert result["total"] == 16  # Issue #3687; schema checklist above.
    assert result["percentage"] == 100.0  # Hand calculation: 16 / 16 * 100.


def test_partial_fixture_score_matches_hand_calculation(
    audit_module, checklist, tmp_path
):
    # Numerator = 5: metadata, inputs, methodology, outputs, scope.
    # Denominator = 16 (issue #3687 and cited schema); 5 / 16 * 100 = 31.25,
    # rounded to one decimal = 31.2 using Python's round-to-even convention.
    content = """\
scope: synthetic
outputs: [synthetic]
methodology: {description: synthetic}
inputs: [synthetic]
metadata: {description: synthetic}
references: []
charts: null
unrelated: synthetic
"""
    result = audit_module.audit_file(write_yaml(tmp_path, content))
    expected_present = ["metadata", "inputs", "methodology", "outputs", "scope"]
    assert result["present"] == expected_present
    assert result["missing"] == [n for n in checklist if n not in expected_present]
    assert len(result["present"]) == 5
    assert result["total"] == 16
    assert result["percentage"] == 31.2


@pytest.mark.parametrize("empty", [None, "", " \n\t", [], {}])
def test_empty_sections_are_missing(audit_module, checklist, empty):
    result = audit_module.audit({name: empty for name in checklist})
    assert result["present"] == []
    assert result["missing"] == checklist
    assert result["percentage"] == 0.0  # Hand calculation: 0 / 16 * 100.


@pytest.mark.parametrize("nonempty", [0, False, "synthetic", [None], {"item": None}])
def test_presence_does_not_validate_nested_content(audit_module, nonempty):
    # Scalars (including zero and false) and nonempty containers are present;
    # no claim is made about their types or nested field validity.
    result = audit_module.audit({"metadata": nonempty})
    assert result["present"] == ["metadata"]
    assert result["percentage"] == 6.2  # Hand calculation: 1 / 16 * 100 = 6.25.


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("metadata: [", "Invalid YAML"),
        ("metadata: !!python/object:unexpected {}", "Invalid YAML"),
        ("{}\n---\n{}", "Invalid YAML"),
        ("", "root must be a mapping"),
        ("null", "root must be a mapping"),
        ("[]", "root must be a mapping"),
        ("synthetic", "root must be a mapping"),
        ("false", "root must be a mapping"),
    ],
)
def test_invalid_yaml_and_nonmapping_fail(audit_module, tmp_path, content, message):
    path = write_yaml(tmp_path, content)
    with pytest.raises(ValueError, match=message):
        audit_module.audit_file(path)
    result = run_cli(path, tmp_path)
    assert result.returncode != 0
    assert result.stdout == ""
    assert message in result.stderr
    assert "Traceback" not in result.stderr
    assert str(path) not in result.stderr


def test_audit_does_not_modify_input(audit_module, tmp_path):
    path = write_yaml(tmp_path, "# preserve comment\nmetadata: {description: synthetic}\n")
    before = path.read_bytes()
    schema_before = SCHEMA.read_bytes()
    audit_module.audit_file(path)
    assert run_cli(path, tmp_path).returncode == 0
    assert path.read_bytes() == before
    assert SCHEMA.read_bytes() == schema_before
    assert list(tmp_path.iterdir()) == [path]


def test_cli_emits_stable_json_in_schema_order(tmp_path):
    path = write_yaml(tmp_path, "scope: synthetic\nmetadata: synthetic\n")
    first = run_cli(path, tmp_path)
    path.write_text("metadata: synthetic\nscope: synthetic\n", encoding="utf-8")
    second = run_cli(path, tmp_path)
    assert first.returncode == second.returncode == 0
    assert first.stderr == second.stderr == ""
    assert first.stdout == second.stdout
    result = json.loads(first.stdout)
    assert set(result) == {"present", "missing", "total", "percentage", "notice"}
    assert result["present"] == ["metadata", "scope"]
    assert result["total"] == 16  # Issue #3687 and cited schema.
    assert result["percentage"] == 12.5  # Hand calculation: 2 / 16 * 100.
    assert "presence is not engineering validation" in result["notice"].lower()


def test_checklist_is_derived_from_schema(audit_module, tmp_path, monkeypatch):
    # Synthetic policy changes both groups; no section names or size may be fixed.
    schema = tmp_path / "schema.yaml"
    schema.write_text(
        "required_fields:\n  synthetic_required: {}\n"
        "optional_sections:\n  synthetic_optional: {}\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(audit_module, "SCHEMA_PATH", schema)
    result = audit_module.audit({"synthetic_optional": "synthetic", "metadata": "extra"})
    assert result["present"] == ["synthetic_optional"]
    assert result["missing"] == ["synthetic_required"]
    assert result["total"] == 2  # Two sections in the synthetic policy above.
    assert result["percentage"] == 50.0  # Hand calculation: 1 / 2 * 100.


def test_missing_input_fails_without_traceback(tmp_path):
    result = run_cli(tmp_path / "absent.yaml", tmp_path)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "Cannot read input" in result.stderr
    assert "Traceback" not in result.stderr
    assert str(tmp_path) not in result.stderr
